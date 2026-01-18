<h1 align="center">CyberDock</h1>

<p align="center">
  Welcome to CyberDock, my custom 3D printed Macropad that runs KMK or QMK firmware.
</p>

<p align="center">
  <img width="520" height="324" alt="Main" src="https://github.com/user-attachments/assets/a0146572-5f79-448c-ac14-118d5b12a648" />
</p>

<p align="center">
  <img width="492" height="671" alt="Exploded" src="https://github.com/user-attachments/assets/d0a7c135-8f6a-44a4-baa8-cb78e2e79458" />
</p>

<hr>

<h2>Bill of Materials:</h2>

<ul>
  <li>1x CyberDock PCB</li>
  <li>1x XIAO-PR2040-DIP</li>
  <li>1x EC11 rotary encoder</li>
  <li>11x Cherry MX (or equivalent) keyswitches</li>
  <li>11x Keycaps</li>
  <li>12x 1N4148 Throughhole diodes</li>
  <li>1x 0.91 inch OLED display (SSD1306 I2C 0.91 128x32)</li>
  <li>4x Cap head M3x16 machine screws</li>
  <li>1x 3D printed shell top half</li>
  <li>1x 3D printed shell bottom half</li>
</ul>

<p>
  small amount of spare wire apprx. 200mm worth.
</p>

<hr>

<h2>Instructions for Assembly:</h2>

<ol>
  <li>Solder RP2040 directly onto the pcb without a header.</li>
  <li>Solder on Diodes aligning with the slikscreen.</li>
  <li>Solder CherryMX switches to board.</li>
  <li>
    Solder breakout cables to the spare 4 pins near the RP2040, these will be used to wire to the OLED display.
    Make these breakout cables ~2" to allow for easier soledering.
  </li>
  <li>
    Clamshell the base around the PCB, passing the breakout cables through the small hole in the gap for the display
    in the top half of the case, then use the M3x16 machine screws to clamp the assembly together.
  </li>
  <li>Solder display to the breakout cables</li>
  <li>Use double-sided tape or a light adhesive to hold the OLED into its holder,.</li>
</ol>


