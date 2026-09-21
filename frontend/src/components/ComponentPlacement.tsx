"use client";

import React, { useState, useMemo } from "react";
import {
  Code,
  Copy,
  Check,
  Download,
  Terminal,
  Cpu,
  RefreshCw,
  Sliders,
  CheckCircle2,
  Crosshair,
  FileCode,
  Sparkles,
  Zap
} from "lucide-react";
import {
  synthesizeProjectPinouts,
  generateMicrocontrollerFirmware,
  MCUPlatform,
  MCU_PROFILES,
  ProjectPinoutData
} from "@/utils/pcbPinoutGenerator";

export interface ComponentPlacementItem {
  ref: string;
  part: string;
  package: string;
  x: number;
  y: number;
  rotation: number;
  layer: string;
  status: "PLACED" | "UNPLACED" | "LOCKED";
}

export interface ComponentPlacementProps {
  components?: ComponentPlacementItem[];
  projectComponents?: any[];
  projectName?: string;
  systemSpecification?: string;
  pinMapping?: any[];
  onMoveComponent?: (ref: string, x: number, y: number) => void;
}

export const ComponentPlacement: React.FC<ComponentPlacementProps> = ({
  components = [],
  projectComponents = [],
  projectName = "Hardware Project",
  systemSpecification = "",
  pinMapping,
  onMoveComponent,
}) => {
  // Synthesize pinout data
  const pinoutData: ProjectPinoutData = useMemo(() => {
    return synthesizeProjectPinouts(projectComponents, projectName, systemSpecification);
  }, [projectComponents, projectName, systemSpecification]);

  // Selected MCU Platform (defaults to detected MCU)
  const [selectedPlatform, setSelectedPlatform] = useState<MCUPlatform>(pinoutData.detectedMCU);
  const [copied, setCopied] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<"code" | "coords">("code");

  // Keep selectedPlatform in sync if detectedMCU changes
  React.useEffect(() => {
    setSelectedPlatform(pinoutData.detectedMCU);
  }, [pinoutData.detectedMCU]);

  // Generate compilable firmware code
  const generatedCode = useMemo(() => {
    return generateMicrocontrollerFirmware(selectedPlatform, pinoutData, projectName);
  }, [selectedPlatform, pinoutData, projectName]);

  const activeMCUProfile = MCU_PROFILES[selectedPlatform];

  // Copy to clipboard
  const handleCopyCode = async () => {
    try {
      await navigator.clipboard.writeText(generatedCode);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    } catch (e) {
      console.error("Failed to copy:", e);
    }
  };

  // Download code file
  const handleDownloadCode = () => {
    let filename = `${projectName.toLowerCase().replace(/\\s+/g, "_")}`;
    let mimeType = "text/plain;charset=utf-8;";

    if (selectedPlatform === "esp32") {
      filename += "_firmware.ino";
    } else if (selectedPlatform === "raspberry_pi") {
      filename += "_controller.py";
    } else if (selectedPlatform === "arduino") {
      filename += "_arduino.ino";
    } else if (selectedPlatform === "stm32") {
      filename += "_main.c";
    }

    const blob = new Blob([generatedCode], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const hasPlacementCoords = Array.isArray(components) && components.length > 0;

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 flex flex-col gap-5 text-zinc-100 shadow-xl">
      {/* Header with Title and Platform Switcher */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between pb-4 border-b border-zinc-800 gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-emerald-950/60 border border-emerald-500/40 flex items-center justify-center text-emerald-400">
            <Code className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h3 className="text-base font-bold text-zinc-100">
                Microcontroller Firmware & Pin Integration Engine
              </h3>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-semibold bg-indigo-950/80 border border-indigo-500/40 text-indigo-300 flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3 text-cyan-400" />
                PIN-SYNCHRONIZED
              </span>
            </div>
            <p className="text-xs text-zinc-400 mt-0.5">
              Production-ready firmware initializing the exact pin configurations defined in the interconnect matrix above
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2 flex-wrap">
          {hasPlacementCoords && (
            <div className="bg-zinc-950 border border-zinc-800 p-0.5 rounded-lg flex text-xs mr-2">
              <button
                onClick={() => setActiveTab("code")}
                className={`px-2.5 py-1 rounded font-medium transition ${
                  activeTab === "code"
                    ? "bg-indigo-600 text-white shadow"
                    : "text-zinc-400 hover:text-zinc-200"
                }`}
              >
                Firmware Code
              </button>
              <button
                onClick={() => setActiveTab("coords")}
                className={`px-2.5 py-1 rounded font-medium transition ${
                  activeTab === "coords"
                    ? "bg-indigo-600 text-white shadow"
                    : "text-zinc-400 hover:text-zinc-200"
                }`}
              >
                Placement Table
              </button>
            </div>
          )}

          <button
            onClick={handleCopyCode}
            className="px-3 py-1.5 rounded-lg bg-zinc-950 border border-zinc-700/80 hover:border-zinc-500 text-xs font-mono text-zinc-200 flex items-center gap-1.5 transition cursor-pointer"
          >
            {copied ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-400" />
                <span className="text-emerald-400 font-semibold">Copied to Clipboard!</span>
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5 text-zinc-400" />
                <span>Copy Code</span>
              </>
            )}
          </button>

          <button
            onClick={handleDownloadCode}
            className="px-3 py-1.5 rounded-lg bg-indigo-950/60 border border-indigo-600/60 hover:bg-indigo-900/80 text-xs font-mono text-indigo-200 flex items-center gap-1.5 transition cursor-pointer"
          >
            <Download className="w-3.5 h-3.5 text-indigo-400" />
            <span>Download Source</span>
          </button>
        </div>
      </div>

      {activeTab === "coords" && hasPlacementCoords ? (
        /* Legacy Placement Table View */
        <div className="overflow-x-auto border border-zinc-800 rounded-lg">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-zinc-950 text-zinc-400 border-b border-zinc-800">
              <tr>
                <th className="p-2.5">Designator</th>
                <th className="p-2.5">Part Name</th>
                <th className="p-2.5">Package</th>
                <th className="p-2.5">Position (X, Y)</th>
                <th className="p-2.5">Rotation</th>
                <th className="p-2.5">Layer</th>
                <th className="p-2.5">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800 bg-zinc-900">
              {components.map((c) => (
                <tr key={c.ref} className="hover:bg-zinc-800/40 transition">
                  <td className="p-2.5 font-bold text-indigo-300">{c.ref}</td>
                  <td className="p-2.5 text-zinc-200">{c.part}</td>
                  <td className="p-2.5 text-zinc-400">{c.package}</td>
                  <td className="p-2.5 text-zinc-300">
                    ({c.x.toFixed(1)}, {c.y.toFixed(1)}) mm
                  </td>
                  <td className="p-2.5 text-zinc-400">{c.rotation}°</td>
                  <td className="p-2.5 text-zinc-300">{c.layer}</td>
                  <td className="p-2.5">
                    <span className="px-1.5 py-0.5 rounded text-[10px] bg-emerald-950/50 text-emerald-400">
                      {c.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        /* Microcontroller Firmware Code View */
        <div className="space-y-4">
          {/* Platform Selector Tabs */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-zinc-950/80 p-2.5 rounded-xl border border-zinc-800">
            <div className="flex items-center gap-1.5 overflow-x-auto">
              {[
                { id: "esp32", label: "ESP32", sub: "C++ / Arduino Core", icon: "⚡" },
                { id: "raspberry_pi", label: "Raspberry Pi", sub: "Python 3 / smbus2", icon: "🍓" },
                { id: "arduino", label: "Arduino", sub: "C++ / AVR Uno/Nano", icon: "♾️" },
                { id: "stm32", label: "STM32", sub: "C / STM32Cube HAL", icon: "🦾" },
              ].map((p) => {
                const isSelected = selectedPlatform === p.id;
                const isDetected = pinoutData.detectedMCU === p.id;
                return (
                  <button
                    key={p.id}
                    onClick={() => setSelectedPlatform(p.id as MCUPlatform)}
                    className={`px-3 py-2 rounded-lg text-xs font-mono transition flex items-center gap-2 whitespace-nowrap cursor-pointer ${
                      isSelected
                        ? "bg-indigo-600 text-white font-bold shadow-md ring-1 ring-indigo-400"
                        : "bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-zinc-200 hover:border-zinc-700"
                    }`}
                  >
                    <span className="text-sm">{p.icon}</span>
                    <div className="text-left">
                      <div className="leading-tight flex items-center gap-1.5">
                        {p.label}
                        {isDetected && (
                          <span className="text-[9px] px-1 py-0.2 rounded bg-emerald-950/90 border border-emerald-500/40 text-emerald-300 font-normal">
                            Detected
                          </span>
                        )}
                      </div>
                      <div className={`text-[10px] ${isSelected ? "text-indigo-200" : "text-zinc-500"}`}>
                        {p.sub}
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Platform Hardware Badge */}
            <div className="flex items-center gap-2 text-xs font-mono text-zinc-400 px-2 py-1 bg-zinc-900 rounded-lg border border-zinc-800">
              <Cpu className="w-3.5 h-3.5 text-indigo-400 flex-shrink-0" />
              <span className="text-zinc-200 font-semibold">{activeMCUProfile.name}</span>
            </div>
          </div>

          {/* Synchronized Pin Assignment Summary Bar */}
          <div className="bg-zinc-950/60 border border-zinc-800/80 rounded-lg p-3 grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs font-mono">
            <div className="bg-zinc-900/80 border border-zinc-800 p-2 rounded">
              <div className="text-[10px] text-zinc-500">I2C BUS PINS</div>
              <div className="font-bold text-cyan-400 mt-0.5">
                SDA: {activeMCUProfile.defaultPins.i2c_sda.gpio} (Pin {activeMCUProfile.defaultPins.i2c_sda.pin})
              </div>
              <div className="font-bold text-cyan-400">
                SCL: {activeMCUProfile.defaultPins.i2c_scl.gpio} (Pin {activeMCUProfile.defaultPins.i2c_scl.pin})
              </div>
            </div>

            <div className="bg-zinc-900/80 border border-zinc-800 p-2 rounded">
              <div className="text-[10px] text-zinc-500">CAN / COMMS PINS</div>
              <div className="font-bold text-amber-400 mt-0.5">
                TX: {activeMCUProfile.defaultPins.can_tx.gpio} (Pin {activeMCUProfile.defaultPins.can_tx.pin})
              </div>
              <div className="font-bold text-amber-400">
                RX: {activeMCUProfile.defaultPins.can_rx.gpio} (Pin {activeMCUProfile.defaultPins.can_rx.pin})
              </div>
            </div>

            <div className="bg-zinc-900/80 border border-zinc-800 p-2 rounded">
              <div className="text-[10px] text-zinc-500">HARDWARE INTERRUPTS</div>
              <div className="font-bold text-emerald-400 mt-0.5">
                BMS: {activeMCUProfile.defaultPins.alert_bms.gpio} (Pin {activeMCUProfile.defaultPins.alert_bms.pin})
              </div>
              <div className="font-bold text-emerald-400">
                INA: {activeMCUProfile.defaultPins.alert_ina.gpio} (Pin {activeMCUProfile.defaultPins.alert_ina.pin})
              </div>
            </div>

            <div className="bg-zinc-900/80 border border-zinc-800 p-2 rounded">
              <div className="text-[10px] text-zinc-500">POWER & GROUND</div>
              <div className="font-bold text-rose-400 mt-0.5">
                VCC: Pin {activeMCUProfile.defaultPins.power_3v3.pin} (3.3V)
              </div>
              <div className="font-bold text-zinc-400">
                GND: Pin {activeMCUProfile.defaultPins.gnd.pin} (Plane)
              </div>
            </div>
          </div>

          {/* Code Editor Preview Window */}
          <div className="relative rounded-xl border border-zinc-800 bg-zinc-950 overflow-hidden shadow-2xl">
            {/* Editor Window Title Bar */}
            <div className="flex items-center justify-between px-4 py-2.5 bg-zinc-900/90 border-b border-zinc-800 text-xs font-mono text-zinc-400">
              <div className="flex items-center gap-2">
                <div className="flex items-center gap-1.5 mr-2">
                  <div className="w-2.5 h-2.5 rounded-full bg-rose-500/80" />
                  <div className="w-2.5 h-2.5 rounded-full bg-amber-500/80" />
                  <div className="w-2.5 h-2.5 rounded-full bg-emerald-500/80" />
                </div>
                <FileCode className="w-3.5 h-3.5 text-indigo-400" />
                <span className="text-zinc-200">
                  {selectedPlatform === "esp32"
                    ? "esp32_firmware.ino"
                    : selectedPlatform === "raspberry_pi"
                    ? "rpi_controller.py"
                    : selectedPlatform === "arduino"
                    ? "arduino_firmware.ino"
                    : "stm32_main.c"}
                </span>
              </div>

              <div className="flex items-center gap-3">
                <span className="text-[11px] text-zinc-500">
                  {generatedCode.split("\n").length} lines • UTF-8
                </span>
                <button
                  onClick={handleCopyCode}
                  className="hover:text-zinc-200 transition flex items-center gap-1 cursor-pointer"
                >
                  <Copy className="w-3 h-3" />
                  <span>{copied ? "Copied" : "Copy"}</span>
                </button>
              </div>
            </div>

            {/* Code Body with Line Numbers */}
            <div className="overflow-x-auto max-h-[500px] overflow-y-auto bg-[#0d1117] rounded-b-xl">
              <div className="min-w-full table text-xs font-mono leading-5">
                {generatedCode.split("\n").map((line, idx) => (
                  <div key={idx} className="table-row group hover:bg-zinc-800/30">
                    <span className="table-cell pl-4 pr-3 text-zinc-600 select-none text-right text-[11px] align-top w-12 border-r border-zinc-800/60">
                      {idx + 1}
                    </span>
                    <span
                      className={`table-cell pl-4 pr-4 whitespace-pre align-top ${
                        line.startsWith("//") || line.startsWith("/*") || line.startsWith(" *") || line.startsWith('"""') || line.startsWith("# ")
                          ? "text-zinc-500 italic"
                          : line.includes("#define") || line.includes("import ") || line.includes("#include") || line.includes("const ")
                          ? "text-purple-400"
                          : line.includes("void ") || line.includes("def ") || line.includes("int ") || line.includes("uint") || line.includes("float ")
                          ? "text-cyan-300 font-semibold"
                          : line.includes("Serial.") || line.includes("logging.") || line.includes("Wire.") || line.includes("GPIO.") || line.includes("HAL_")
                          ? "text-amber-300"
                          : "text-zinc-200"
                      }`}
                    >
                      {line || "\u00A0"}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
