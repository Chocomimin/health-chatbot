// src/components/MapView.jsx
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { useEffect, useState } from 'react';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix default marker icon issues
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl:
    'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl:
    'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

export default function MapView() {
  const [userLocation, setUserLocation] = useState(null);
  const [places, setPlaces] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const fallbackLocation = [16.9891, 82.2475]; // 📍 Kakinada coordinates

    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const coords = [pos.coords.latitude, pos.coords.longitude];
        setUserLocation(coords);
        await fetchNearbyPlaces(coords);
      },
      async () => {
        setError("⚠️ Location access denied. Showing Kakinada.");
        setUserLocation(fallbackLocation);
        await fetchNearbyPlaces(fallbackLocation);
      }
    );
  }, []);

  const fetchNearbyPlaces = async ([latitude, longitude]) => {
    const query = `
      [out:json][timeout:25];
      (
        node["amenity"="hospital"](around:5000,${latitude},${longitude});
        node["amenity"="clinic"](around:5000,${latitude},${longitude});
      );
      out body;
    `;

    try {
      const res = await fetch('https://overpass-api.de/api/interpreter', {
        method: 'POST',
        body: query,
      });
      const data = await res.json();
      setPlaces(data.elements || []);
    } catch (err) {
      setError("⚠️ Unable to load nearby hospitals.");
    }
  };

  if (!userLocation) {
    return <p style={{ textAlign: "center", marginTop: "1rem" }}>📍 Detecting your location...</p>;
  }

  return (
    <div style={{ marginTop: "2rem", border: "1px solid #ddd", borderRadius: "10px", overflow: "hidden" }}>
      {error && <p style={{ textAlign: "center", color: "#dc3545" }}>{error}</p>}
      <MapContainer center={userLocation} zoom={14} style={{ height: '90%', width: '100%' }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        <Marker position={userLocation}>
          <Popup>📍 You are here</Popup>
        </Marker>
        {places.map((place, i) => (
          <Marker key={i} position={[place.lat, place.lon]}>
            <Popup>
              <strong>{place.tags.name || 'Unnamed'}</strong><br />
              {place.tags.amenity}
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
