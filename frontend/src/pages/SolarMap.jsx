import { useState, useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import iconUrl from "leaflet/dist/images/marker-icon.png";
import iconRetinaUrl from "leaflet/dist/images/marker-icon-2x.png";
import shadowUrl from "leaflet/dist/images/marker-shadow.png";

import {
  MapPin,
  Search,
  Navigation,
  Compass,
  AlertCircle,
  Loader2,
  Globe,
} from "lucide-react";

// Fix Leaflet marker icon asset paths for Vite bundler
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconUrl,
  iconRetinaUrl,
  shadowUrl,
});

export default function SolarMap() {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const markerRef = useRef(null);

  const [searchQuery, setSearchQuery] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [searchError, setSearchError] = useState(null);
  const [isLocating, setIsLocating] = useState(false);
  const [locationError, setLocationError] = useState(null);

  const [selectedLocation, setSelectedLocation] = useState({
    name: "Pavagada Solar Park (Karnataka)",
    lat: 14.0957,
    lon: 77.2798,
    type: "Solar Installation Site",
  });

  // Notable solar facilities for quick selection
  const solarFacilities = [
    {
      name: "Pavagada Solar Park (Karnataka)",
      lat: 14.0957,
      lon: 77.2798,
      region: "Tumkur, India",
    },
    {
      name: "Bhadla Solar Park (Rajasthan)",
      lat: 27.5392,
      lon: 71.9167,
      region: "Jodhpur, India",
    },
    {
      name: "Kurnool Ultra Mega Solar Park (AP)",
      lat: 15.6811,
      lon: 78.2831,
      region: "Kurnool, India",
    },
    {
      name: "Noor Complex Solar Facility",
      lat: 30.9983,
      lon: -6.8617,
      region: "Ouarzazate, Morocco",
    },
  ];

  // Initialize Leaflet Map
  useEffect(() => {
    if (!mapContainerRef.current) return;

    if (!mapInstanceRef.current) {
      const map = L.map(mapContainerRef.current, {
        center: [selectedLocation.lat, selectedLocation.lon],
        zoom: 12,
        zoomControl: true,
      });

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      }).addTo(map);

      const marker = L.marker([selectedLocation.lat, selectedLocation.lon])
        .addTo(map)
        .bindPopup(`<b>${selectedLocation.name}</b><br/>Lat: ${selectedLocation.lat.toFixed(4)}, Lon: ${selectedLocation.lon.toFixed(4)}`)
        .openPopup();

      markerRef.current = marker;

      // Handle map click to place/move marker
      map.on("click", (e) => {
        const { lat, lng } = e.latlng;
        marker.setLatLng([lat, lng]);
        marker.bindPopup(`<b>Selected Coordinates</b><br/>Lat: ${lat.toFixed(4)}, Lon: ${lng.toFixed(4)}`).openPopup();
        setSelectedLocation({
          name: `Custom Location (${lat.toFixed(4)}, ${lng.toFixed(4)})`,
          lat,
          lon: lng,
          type: "User Selected Pin",
        });
        setLocationError(null);
      });

      mapInstanceRef.current = map;
      setTimeout(() => {
        map.invalidateSize();
      }, 250);
    }

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Update map and marker when selectedLocation changes
  const updateMapPosition = (lat, lon, name, zoom = 14) => {
    if (mapInstanceRef.current && markerRef.current) {
      mapInstanceRef.current.flyTo([lat, lon], zoom, { duration: 1.2 });
      markerRef.current.setLatLng([lat, lon]);
      markerRef.current.bindPopup(`<b>${name}</b><br/>Lat: ${lat.toFixed(4)}, Lon: ${lon.toFixed(4)}`).openPopup();
    }
  };

  // Facility Preset Selection
  const handleSelectFacility = (facility) => {
    setSelectedLocation({
      name: facility.name,
      lat: facility.lat,
      lon: facility.lon,
      type: "Registered Solar PV Site",
    });
    setSearchError(null);
    setLocationError(null);
    updateMapPosition(facility.lat, facility.lon, facility.name, 13);
  };

  // Search Location via OpenStreetMap Nominatim Geocoding API
  const handleSearch = async (e) => {
    e?.preventDefault();
    const query = searchQuery.trim();
    if (!query) return;

    setIsSearching(true);
    setSearchError(null);
    setLocationError(null);

    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1`
      );
      if (!response.ok) throw new Error("Search service request failed");

      const data = await response.json();
      if (!data || data.length === 0) {
        setSearchError(`No coordinates found for "${query}". Try another location name.`);
        return;
      }

      const place = data[0];
      const lat = parseFloat(place.lat);
      const lon = parseFloat(place.lon);

      setSelectedLocation({
        name: place.display_name.split(",").slice(0, 3).join(","),
        lat,
        lon,
        type: "Geocoded Location",
      });

      updateMapPosition(lat, lon, place.display_name.split(",")[0], 14);
    } catch (err) {
      setSearchError(err.message || "Failed to search location. Check internet connection.");
    } finally {
      setIsSearching(false);
    }
  };

  // Request Current Location via Browser Geolocation API
  const handleLocateMe = () => {
    if (!navigator.geolocation) {
      setLocationError("Geolocation is not supported by your browser.");
      return;
    }

    setIsLocating(true);
    setLocationError(null);
    setSearchError(null);

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const lat = position.coords.latitude;
        const lon = position.coords.longitude;

        setSelectedLocation({
          name: "Current GPS Location",
          lat,
          lon,
          type: "User Device Location",
        });

        updateMapPosition(lat, lon, "Your Current Location", 15);
        setIsLocating(false);
      },
      (error) => {
        setIsLocating(false);
        switch (error.code) {
          case error.PERMISSION_DENIED:
            setLocationError("Location permission was denied. Please allow location access in browser settings.");
            break;
          case error.POSITION_UNAVAILABLE:
            setLocationError("Location information is currently unavailable.");
            break;
          case error.TIMEOUT:
            setLocationError("Request to get your location timed out. Try again.");
            break;
          default:
            setLocationError("An error occurred while retrieving your location.");
            break;
        }
      },
      { timeout: 10000, enableHighAccuracy: true }
    );
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2.5">
            Solar Site Map
            <span className="text-[11px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200">
              Live GIS Layer
            </span>
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
            Geospatial interactive mapping for solar photovoltaic array sites & installations
          </p>
        </div>

        <button
          onClick={handleLocateMe}
          disabled={isLocating}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs shadow-xs transition disabled:opacity-50"
        >
          {isLocating ? (
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <Navigation className="w-3.5 h-3.5 text-emerald-400" />
          )}
          <span>{isLocating ? "Requesting GPS..." : "Locate Me"}</span>
        </button>
      </div>

      {/* Honest Backend Disclaimer: No Fake Analytics Banner */}
      <div className="p-4 rounded-2xl bg-amber-50/80 border border-amber-200 text-amber-900 text-xs sm:text-sm flex items-start gap-3">
        <AlertCircle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
        <div>
          <p className="font-bold text-amber-950">Geospatial Solar Telemetry Status</p>
          <p className="text-amber-800 text-xs mt-0.5 leading-relaxed">
            Solar analytics are not available from the current backend. The map is fully functional for spatial navigation, geocoding, and solar site coordinates without fabricating artificial irradiance or yield values.
          </p>
        </div>
      </div>

      {/* Main Grid: Controls (4 cols) & Interactive Map Canvas (8 cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Location Search & Presets */}
        <div className="lg:col-span-4 space-y-4">
          {/* Search Card */}
          <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-5 space-y-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Search Solar Site / Location
            </h3>

            <form onSubmit={handleSearch} className="space-y-2">
              <div className="relative">
                <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Enter city, address, or park name..."
                  className="w-full pl-9 pr-20 py-2.5 rounded-xl border border-slate-200 text-xs sm:text-sm text-slate-900 placeholder:text-slate-400 focus:outline-hidden focus:ring-2 focus:ring-emerald-500 transition"
                />
                <button
                  type="submit"
                  disabled={isSearching || !searchQuery.trim()}
                  className="absolute right-1.5 top-1/2 -translate-y-1/2 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs transition disabled:opacity-40"
                >
                  {isSearching ? <Loader2 className="w-3 h-3 animate-spin" /> : "Search"}
                </button>
              </div>

              {searchError && (
                <p className="text-xs text-rose-600 font-medium pt-1">{searchError}</p>
              )}
              {locationError && (
                <p className="text-xs text-rose-600 font-medium pt-1">{locationError}</p>
              )}
            </form>

            {/* Presets List */}
            <div className="space-y-2 pt-2 border-t border-slate-100">
              <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                Major Solar PV Sites
              </p>
              <div className="space-y-1.5">
                {solarFacilities.map((facility, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSelectFacility(facility)}
                    className={`w-full text-left p-2.5 rounded-xl border text-xs transition flex items-center justify-between ${
                      selectedLocation.name === facility.name
                        ? "bg-emerald-50 border-emerald-300 text-emerald-950 font-semibold shadow-xs"
                        : "bg-slate-50 hover:bg-slate-100 border-slate-200/70 text-slate-700"
                    }`}
                  >
                    <div className="truncate pr-2">
                      <span className="font-bold block truncate">{facility.name}</span>
                      <span className="text-[10px] text-slate-500">{facility.region}</span>
                    </div>
                    <MapPin className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Selected Coordinates Card */}
          <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-5 space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
              <Compass className="w-3.5 h-3.5 text-slate-400" />
              Selected Coordinates
            </h4>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">Site / Label</span>
                <span className="font-semibold text-slate-900 text-right max-w-[180px] truncate">
                  {selectedLocation.name}
                </span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">Latitude</span>
                <span className="font-mono font-bold text-emerald-700">
                  {selectedLocation.lat.toFixed(6)}°
                </span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">Longitude</span>
                <span className="font-mono font-bold text-emerald-700">
                  {selectedLocation.lon.toFixed(6)}°
                </span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">GIS Source</span>
                <span className="font-semibold text-slate-700">OpenStreetMap (OSM)</span>
              </div>
              <div className="flex justify-between py-1.5 text-amber-800 bg-amber-50/60 px-2 rounded-lg">
                <span className="text-slate-600">Solar Analytics</span>
                <span className="font-medium text-[11px]">Not available in backend</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Leaflet Interactive Map Container */}
        <div className="lg:col-span-8 space-y-3">
          <div className="bg-white rounded-3xl border border-slate-200/80 shadow-md p-2 overflow-hidden relative">
            {/* Real Leaflet Map DOM Canvas */}
            <div
              ref={mapContainerRef}
              className="w-full h-[480px] rounded-2xl z-0"
              style={{ minHeight: "480px" }}
            />

            {/* Map floating info pill */}
            <div className="absolute top-5 left-5 z-[1000] bg-white/90 backdrop-blur-md px-3 py-1.5 rounded-xl border border-slate-200 shadow-sm flex items-center gap-2 text-xs font-semibold text-slate-800">
              <Globe className="w-3.5 h-3.5 text-emerald-600" />
              <span>Click map to place or reposition pin</span>
            </div>
          </div>

          <div className="flex items-center justify-between text-[11px] text-slate-400 px-2">
            <span>Tile Source: © OpenStreetMap contributors</span>
            <span>Zoom & Pan enabled</span>
          </div>
        </div>
      </div>
    </div>
  );
}