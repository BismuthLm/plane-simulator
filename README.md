# Top-Down Plane Simulator

A simple yet engaging 2D plane simulator built with Python and Pygame. Navigate through a procedurally generated world with rivers, forests, lakes, and a central runway.

![Plane Simulator Screenshot](screenshots/screenshot.png)

## Features

- Top-down view plane simulation
- Procedurally generated terrain:
  - Winding rivers
  - Dense forest clusters
  - Scattered trees
  - Lakes and water bodies
  - Central runway
- Smooth plane controls
- Real-time speed indicator
- Infinite world exploration

## Installation

1. Ensure you have Python 3.8+ installed
2. Clone this repository:
   ```bash
   git clone https://github.com/BismuthLm/plane-simulator.git
   cd plane-simulator
   ```
3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## How to Play

Run the simulator:
```bash
python plane_simulator.py
```

### Controls
- **LEFT/RIGHT Arrow Keys**: Rotate the plane
- **UP Arrow Key**: Increase speed
- **DOWN Arrow Key**: Decrease speed
- **Close Window**: Quit game

## Gameplay Tips

- Take off from the central runway
- Follow rivers for navigation
- Try flying through dense forests (challenging!)
- Practice landing back on the runway
- Explore the procedurally generated world

## Development

The simulator is built using:
- Python 3.8+
- Pygame 2.5.2+
- NumPy 1.26.3+

### Project Structure
```
plane-simulator/
├── plane_simulator.py   # Main game file
├── requirements.txt     # Python dependencies
├── screenshots/         # Game screenshots
├── LICENSE             # MIT License
└── README.md           # This file
```

## Contributing

Contributions are welcome! Feel free to:
1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
