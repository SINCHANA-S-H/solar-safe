import { useState } from "react";
import {
  MapPin,
  Search,
  Sun,
  AlertCircle,
  Compass,
  Globe,
  Navigation,
} from "lucide-react";

export default function SolarMap() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedSite, setSelectedSite] = useState({
    name: "Solar Array Alpha (Rooftop PV)",
    lat: "12.9716° N",
    lon: "77.5946° E",
    installedCapacity: "45 kWp",
    modulesCount: 120,
    status: "Active Inspection Mode",
    simulatedGhi: "5.42 kWh/m²/day",
  });

  const demoSites = [
    {
      name: "Solar Array Alpha (Rooftop PV)",
      lat: "12.9716° N",
      lon: "77.5946° E",
      installedCapacity: "45 kWp",
      modulesCount: 120,
      status: "Active Inspection Mode",
      simulatedGhi: "5.42 kWh/m²/day",
    },
    {
      name: "Commercial Solar Park Beta",
      lat: "13.0827° N",
      lon: "80.2707° E",
      installedCapacity: "250 kWp",
      modulesCount: 680,
      status: "Maintenance Due",
      simulatedGhi: "5.78 kWh/m²/day",
    },
    {
      name: "Industrial Rooftop Gamma",
      lat: "19.0760° N",
      lon: "72.8777° E",
      installedCapacity: "110 kWp",
      modulesCount: 310,
      status: "Active Inspection Mode",
      simulatedGhi: "5.15 kWh/m²/day",
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2.5">
            Solar Geospatial Mapping
            <span className="text-[11px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-amber-100 text-amber-800 border border-amber-200">
              Simulation Layer
            </span>
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
            GIS spatial mapping & solar irradiance potential architecture
          </p>
        </div>
      </div>

      {/* Transparency / Disclaimer Banner */}
      <div className="p-4 rounded-2xl bg-amber-50/70 border border-amber-200/80 text-amber-900 text-xs sm:text-sm flex items-start gap-3">
        <AlertCircle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
        <div>
          <p className="font-bold text-amber-900">GIS & Irradiance Integration Architecture</p>
          <p className="text-amber-800/90 text-xs mt-0.5 leading-relaxed">
            Live satellite solar irradiance and real-time GIS API telemetry are not currently connected to the backend database. This interactive view displays the modular architecture designed for Leaflet/Mapbox and satellite irradiance providers.
          </p>
        </div>
      </div>

      {/* Main Grid: Controls + Interactive Map Visual Canvas */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Side: Search & Site Selector (4 cols) */}
        <div className="lg:col-span-4 space-y-4">
          <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-5 space-y-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Search Solar Installations
            </h3>
            <div className="relative">
              <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search coordinates or site name..."
                className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-slate-200 text-xs sm:text-sm text-slate-900 placeholder:text-slate-400 focus:outline-hidden focus:ring-2 focus:ring-emerald-500 transition"
              />
            </div>

            <div className="space-y-2 pt-2">
              <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                Monitored PV Facilities
              </p>
              {demoSites.map((site, idx) => (
                <button
                  key={idx}
                  onClick={() => setSelectedSite(site)}
                  className={`w-full text-left p-3 rounded-xl border text-xs transition ${
                    selectedSite.name === site.name
                      ? "bg-emerald-50/80 border-emerald-300 text-emerald-950 font-semibold shadow-xs"
                      : "bg-slate-50 hover:bg-slate-100 border-slate-200/70 text-slate-700"
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-bold truncate">{site.name}</span>
                    <span className="text-[10px] bg-white px-1.5 py-0.5 rounded border border-slate-200">
                      {site.installedCapacity}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-[11px] text-slate-500">
                    <MapPin className="w-3 h-3 text-emerald-600" />
                    <span>
                      {site.lat}, {site.lon}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Selected Site Details Card */}
          <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-5 space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
              <Compass className="w-3.5 h-3.5 text-slate-400" />
              Facility Metadata
            </h4>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">Site Name</span>
                <span className="font-semibold text-slate-900">{selectedSite.name}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">Installed Capacity</span>
                <span className="font-bold text-emerald-700">{selectedSite.installedCapacity}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">Total PV Modules</span>
                <span className="font-semibold text-slate-800">{selectedSite.modulesCount} panels</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">Simulated Irradiance (GHI)</span>
                <span className="font-bold text-amber-600">{selectedSite.simulatedGhi}</span>
              </div>
              <div className="flex justify-between py-1.5">
                <span className="text-slate-500">Inspection Status</span>
                <span className="font-semibold text-emerald-600">{selectedSite.status}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Side: Map Canvas Container (8 cols) */}
        <div className="lg:col-span-8 space-y-4">
          <div className="bg-slate-900 rounded-3xl border border-slate-800 shadow-xl overflow-hidden relative min-h-[460px] flex flex-col justify-between p-6">
            {/* Top Toolbar overlay */}
            <div className="flex items-center justify-between z-10">
              <div className="flex items-center gap-2 bg-slate-950/80 backdrop-blur-md px-3 py-1.5 rounded-xl border border-white/10 text-white text-xs font-semibold">
                <Globe className="w-3.5 h-3.5 text-emerald-400" />
                <span>Simulated Satellite Orthophoto Layer</span>
              </div>

              <div className="flex items-center gap-1.5 bg-slate-950/80 backdrop-blur-md px-2.5 py-1.5 rounded-xl border border-white/10 text-slate-300 text-xs">
                <Navigation className="w-3.5 h-3.5 text-amber-400" />
                <span>
                  {selectedSite.lat}, {selectedSite.lon}
                </span>
              </div>
            </div>

            {/* Stylized GIS Grid Map Artwork */}
            <div className="absolute inset-0 flex items-center justify-center opacity-85 pointer-events-none">
              <div className="w-full h-full relative flex items-center justify-center">
                {/* Radial rings */}
                <div className="w-[320px] h-[320px] rounded-full border border-emerald-500/20 absolute animate-pulse-subtle" />
                <div className="w-[480px] h-[480px] rounded-full border border-emerald-500/10 absolute" />
                <div className="w-[620px] h-[620px] rounded-full border border-emerald-500/5 absolute" />

                {/* Grid matrix lines */}
                <div className="absolute inset-0 bg-[radial-gradient(#10b981_1px,transparent_1px)] [background-size:24px_24px] opacity-25" />

                {/* Simulated Solar Panel Array polygon */}
                <div className="relative z-10 bg-emerald-950/70 border border-emerald-500/40 rounded-2xl p-6 shadow-2xl backdrop-blur-xs max-w-sm text-center">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 to-emerald-500 text-white flex items-center justify-center mx-auto mb-3 shadow-lg shadow-emerald-500/30">
                    <Sun className="w-5 h-5 animate-pulse-subtle" />
                  </div>
                  <h4 className="text-white font-bold text-sm tracking-tight">{selectedSite.name}</h4>
                  <p className="text-emerald-300 text-xs mt-1">
                    Solar Yield Estimate: {selectedSite.simulatedGhi}
                  </p>
                  <div className="mt-3 pt-3 border-t border-white/10 flex items-center justify-center gap-4 text-[11px] text-slate-400">
                    <span>Lat: {selectedSite.lat}</span>
                    <span>Lon: {selectedSite.lon}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Bottom Legend Overlay */}
            <div className="z-10 flex flex-wrap items-center justify-between gap-3 bg-slate-950/80 backdrop-blur-md p-3 rounded-2xl border border-white/10 text-xs text-white">
              <div className="flex items-center gap-4">
                <span className="text-slate-400 font-bold uppercase tracking-wider text-[10px]">
                  Map Legend
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
                  <span>Normal Panels</span>
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
                  <span>Hotspot Risk</span>
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-rose-500" />
                  <span>Cell Crack Defect</span>
                </span>
              </div>

              <span className="text-[11px] text-slate-400">
                Leaflet / Mapbox integration interface
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}