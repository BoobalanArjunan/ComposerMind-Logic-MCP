import Cocoa
import ApplicationServices

func fail(_ message: String) -> Never {
    FileHandle.standardError.write(Data((message + "\n").utf8))
    exit(1)
}
func attr(_ e: AXUIElement, _ name: String) -> CFTypeRef? {
    var v: CFTypeRef?
    return AXUIElementCopyAttributeValue(e, name as CFString, &v) == .success ? v : nil
}
func find(_ e: AXUIElement, _ depth: Int = 0) -> AXUIElement? {
    guard depth < 30 else { return nil }
    if attr(e, kAXDescriptionAttribute) as? String == "Tempo",
       attr(e, kAXRoleAttribute) as? String == "AXSlider" { return e }
    for child in attr(e, kAXChildrenAttribute) as? [AXUIElement] ?? [] {
        if let found = find(child, depth + 1) { return found }
    }
    return nil
}
let args = CommandLine.arguments
var target: Double? = nil
if args.count == 2 {
    guard let n = Double(args[1]), n.isFinite, n >= 40, n <= 240, n.rounded() == n else {
        fail("Target must be an integer BPM between 40 and 240")
    }
    target = n
} else if args.count != 1 { fail("Usage: tempo.swift [BPM]") }
guard AXIsProcessTrusted() else { fail("Accessibility permission required") }
guard let app = NSWorkspace.shared.runningApplications.first(where: { $0.localizedName == "Logic Pro" }) else {
    fail("Logic Pro not running")
}
app.unhide()
app.activate(options: [])
let ax = AXUIElementCreateApplication(app.processIdentifier)
var control: AXUIElement?
for _ in 1...10 {
    RunLoop.current.run(until: Date().addingTimeInterval(1))
    for window in attr(ax, kAXWindowsAttribute) as? [AXUIElement] ?? [] {
        if let found = find(window) { control = found; break }
    }
    if control != nil { break }
}
guard let tempo = control else { fail("Tempo control not found") }
func readBPM() -> Double {
    guard let n = attr(tempo, kAXValueAttribute) as? NSNumber else { fail("Tempo readback failed") }
    return n.doubleValue
}
let initial = readBPM()
func report(_ bpm: Double, _ iterations: Int) {
    print("{\"initial_bpm\":\(initial),\"bpm\":\(bpm),\"iterations\":\(iterations)}")
}
guard let goal = target else { report(initial, 0); exit(0) }
var writable: DarwinBoolean = false
guard AXUIElementIsAttributeSettable(tempo, kAXValueAttribute as CFString, &writable) == .success,
      writable.boolValue else { fail("Tempo not writable") }
for i in 0...100 {
    let bpm = readBPM()
    let delta = goal - bpm
    if abs(delta) < 0.01 { report(bpm, i); exit(0) }
    if i == 100 { break }
    guard app.isActive else { fail("Logic lost focus") }
    let result: AXError
    if abs(delta) >= 10 {
        result = AXUIElementPerformAction(tempo, (delta > 0 ? kAXIncrementAction : kAXDecrementAction) as CFString)
    } else {
        result = AXUIElementSetAttributeValue(tempo, kAXValueAttribute as CFString, NSNumber(value: goal))
    }
    guard result == .success else { fail("AX operation failed: \(result.rawValue)") }
    RunLoop.current.run(until: Date().addingTimeInterval(0.3))
    guard abs(readBPM() - goal) < abs(delta) else { fail("Tempo adjustment not converging") }
}
fail("Tempo retry limit reached")
