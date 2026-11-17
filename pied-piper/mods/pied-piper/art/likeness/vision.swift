// Finds the face in each picture (outline, eyes, brows, nose, lips) and the
// person's silhouette, with macOS's Vision. Prints one JSON line per picture;
// writes the silhouette as <maskdir>/<name>.png.
//   vision <maskdir> <picture>...
import Foundation
import Vision
import CoreImage

let args = CommandLine.arguments
let maskDir = args[1]
let ctx = CIContext()

func points(_ r: VNFaceLandmarkRegion2D?, _ size: CGSize) -> [[Double]] {
    guard let r = r else { return [] }
    return r.pointsInImage(imageSize: size).map { [Double($0.x), Double(size.height - $0.y)] }
}

for path in args.dropFirst(2) {
    let url = URL(fileURLWithPath: path)
    let name = url.deletingPathExtension().lastPathComponent
    guard let src = CGImageSourceCreateWithURL(url as CFURL, nil),
          let cg = CGImageSourceCreateImageAtIndex(src, 0, nil) else {
        print("{\"name\": \"\(name)\", \"error\": \"unreadable\"}"); continue
    }
    let size = CGSize(width: cg.width, height: cg.height)
    let handler = VNImageRequestHandler(cgImage: cg, options: [:])
    let faces = VNDetectFaceLandmarksRequest()
    let person = VNGeneratePersonSegmentationRequest()
    person.qualityLevel = .accurate
    person.outputPixelFormat = kCVPixelFormatType_OneComponent8
    var out: [String: Any] = ["name": name, "width": cg.width, "height": cg.height]
    do {
        try handler.perform([faces, person])
        if let buf = person.results?.first?.pixelBuffer {
            let img = CIImage(cvPixelBuffer: buf)
            try ctx.writePNGRepresentation(of: img, to: URL(fileURLWithPath: "\(maskDir)/\(name).png"),
                                           format: .L8, colorSpace: CGColorSpace(name: CGColorSpace.linearGray)!)
            out["mask"] = [CVPixelBufferGetWidth(buf), CVPixelBufferGetHeight(buf)]
        }
        let found = (faces.results ?? []).sorted { $0.boundingBox.width * $0.boundingBox.height > $1.boundingBox.width * $1.boundingBox.height }
        out["faces"] = found.count
        if let f = found.first, let lm = f.landmarks {
            let b = f.boundingBox
            out["box"] = [Double(b.minX) * Double(cg.width), (1 - Double(b.maxY)) * Double(cg.height), Double(b.width) * Double(cg.width), Double(b.height) * Double(cg.height)]
            out["roll"] = f.roll?.doubleValue ?? 0
            out["yaw"] = f.yaw?.doubleValue ?? 0
            out["contour"] = points(lm.faceContour, size)
            out["left_eye"] = points(lm.leftEye, size)
            out["right_eye"] = points(lm.rightEye, size)
            out["left_brow"] = points(lm.leftEyebrow, size)
            out["right_brow"] = points(lm.rightEyebrow, size)
            out["nose"] = points(lm.nose, size)
            out["lips"] = points(lm.outerLips, size)
            out["median"] = points(lm.medianLine, size)
        }
    } catch {
        out["error"] = "\(error)"
    }
    let data = try! JSONSerialization.data(withJSONObject: out, options: [])
    print(String(data: data, encoding: .utf8)!)
}
