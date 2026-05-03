import { useState } from "react";

function App() {
  const [angles, setAngles] = useState({
    0: 90,
    1: 90,
    2: 90,
    3: 90,
  });

  const moveServo = async (channel, angle) => {
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
    } catch (error) {
      console.error("Error moving servo:", error);
    }
  };

  const handleSliderChange = (channel, value) => {
    setAngles((prev) => ({
      ...prev,
      [channel]: Number(value),
    }));
  };

  const sendAngle = (channel) => {
    moveServo(channel, angles[channel]);
  };

  const homeArm = async () => {
    setAngles({
      0: 90,
      1: 90,
      2: 90,
      3: 90,
    });

    await fetch("http://127.0.0.1:8000/control/home", {
      method: "POST",
    });
  };

  const jointNames = {
    0: "Base",
    1: "Shoulder",
    2: "Elbow",
    3: "Wrist",
  };

  return (
    <div style={{ padding: "30px", fontFamily: "Arial" }}>
      <h1>Robotic Arm Control</h1>

      {[0, 1, 2, 3].map((channel) => (
        <div
          key={channel}
          style={{
            border: "1px solid #ccc",
            padding: "15px",
            marginBottom: "15px",
            borderRadius: "8px",
          }}
        >
          <h2>{jointNames[channel]}</h2>

          <input
            type="range"
            min="0"
            max="180"
            value={angles[channel]}
            onChange={(e) => handleSliderChange(channel, e.target.value)}
          />

          <p>Angle: {angles[channel]}°</p>

          <button onClick={() => sendAngle(channel)}>
            Move {jointNames[channel]}
          </button>
        </div>
      ))}

      <button
        onClick={homeArm}
        style={{
          padding: "12px 20px",
          fontSize: "16px",
          marginTop: "20px",
        }}
      >
        Home Arm
      </button>
    </div>
  );
}

export default App;
