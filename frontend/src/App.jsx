import { useState } from "react";

function App() {
  const [angles, setAngles] = useState({
    0: 90,
    1: 90,
    2: 90,
    3: 90,
  });

  const jointNames = {
    0: "Base",
    1: "Shoulder",
    2: "Elbow",
    3: "Wrist",
  };

  const moveServo = async (channel) => {
    const angle = angles[channel];

    try {
      const response = await fetch("http://127.0.0.1:8000/control/move", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          channel: Number(channel),
          angle: Number(angle),
        }),
      });

      const data = await response.json();
      console.log(data);
      alert(`Moved ${jointNames[channel]} to ${angle}°`);
    } catch (error) {
      console.error(error);
      alert("Could not connect to backend yet. This is expected if FastAPI is not running.");
    }
  };

  const handleSliderChange = (channel, value) => {
    setAngles((prev) => ({
      ...prev,
      [channel]: Number(value),
    }));
  };

  return (
    <div style={{ padding: "40px", fontFamily: "Arial", maxWidth: "700px" }}>
      <h1>Robotic Arm Control</h1>
      <p>Use the sliders to choose servo angles.</p>
      <p>Scamuel Bernardo is selling some totally legit Essentials!</p>

      {[0, 1, 2, 3].map((channel) => (
        <div
          key={channel}
          style={{
            border: "1px solid #ccc",
            borderRadius: "10px",
            padding: "20px",
            marginBottom: "16px",
          }}
        >
          <h2>{jointNames[channel]}</h2>

          <input
            type="range"
            min="60"
            max="120"
            value={angles[channel]}
            onChange={(e) => handleSliderChange(channel, e.target.value)}
            style={{ width: "100%" }}
          />

          <p>Angle: {angles[channel]}°</p>

          <button onClick={() => moveServo(channel)}>
            Move {jointNames[channel]}
          </button>
        </div>
      ))}
    </div>
  );
}

export default App;