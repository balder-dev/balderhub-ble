Introduction into Bluetooth Low Energy (BLE) Protocol
*****************************************************

.. todo provide an explanation of your specific topic that can help others to use your BalderHub project


Bluetooth Low Energy (BLE, also called Bluetooth LE) is a wireless personal area network technology developed by the
Bluetooth Special Interest Group (Bluetooth SIG). It was introduced in the Bluetooth Core Specification version
4.0 (2010) as a low-power companion to classic Bluetooth (BR/EDR). While sharing the same 2.4 GHz ISM band, BLE is
optimized for intermittent, short-burst data transfers with ultra-low energy consumption—ideal for battery-powered
sensors, wearables, beacons, fitness devices, and IoT applications that can run for months or years on a coin cell.

Key Features and Design Principles
==================================

* Radio basics: 40 channels (2 MHz spacing) vs. 79 in classic Bluetooth. Uses Gaussian Frequency Shift Keying (GFSK).
* PHY options (for flexibility in speed vs. range):
    * LE 1M PHY (mandatory): 1 Mbit/s
    * LE 2M PHY: 2 Mbit/s (higher throughput)
    * LE Coded PHY (S=2 or S=8): 500 kbit/s or 125 kbit/s (longer range, better robustness)
* Communication topologies:
    * Point-to-point (Central ↔ Peripheral)
    * Broadcast / connectionless (advertising)
    * Mesh (for large-scale networks)
* Power efficiency: Devices spend most time in sleep mode. Advertising and short connection events minimize radio-on
  time. Roles are asymmetric—power-rich centrals (phones, hubs) do more work than peripherals.
* Additional capabilities (since Bluetooth 5.x): Extended advertising, periodic advertising, direction finding
  (AoA/AoD), channel sounding for distance, and isochronous channels (foundation for LE Audio).

BLE supports both connection-oriented (reliable bidirectional data) and connectionless (advertising packets)
communication. Discovery happens via advertising packets on three primary channels; once connected, data flows over the
remaining 37 data channels with adaptive frequency hopping.

For full technical details, refer to the official Bluetooth LE Primer and the Bluetooth Core Specification on
bluetooth.com.


GATT – Generic Attribute Profile
================================

Once a BLE connection is established (handled by the Generic Access Profile – GAP), data exchange is defined by the
Generic Attribute Profile (GATT). GATT sits on top of the Attribute Protocol (ATT) and provides a standardized,
hierarchical way to expose and access device data.

Core Concepts (Client-Server Model)
-----------------------------------

**GATT Server**: Typically the peripheral device. It stores and exposes data in a structured attribute table.
**GATT Client**: Typically the central (e.g., smartphone, hub). It discovers and interacts with the server.

**Hierarchy:**

1) Services
    * Logical groupings of related functionality.
    * Identified by a 16-bit (SIG-defined) or 128-bit (custom) UUID.
    * Examples: Battery Service (0x180F), Heart Rate Service (0x180D), or a custom “SensorHub Service”.

2) Characteristics
    * The actual data containers inside a service.
    * Each has a UUID, a value (byte array), properties (read, write, notify, indicate, write-without-response, etc.), and optional descriptors.
    * Descriptors add metadata (e.g., Client Characteristic Configuration for enabling notifications, User Description, etc.).

3) Profiles
    * A pre-defined collection of services that together implement a complete use case.
    * Defined by the Bluetooth SIG for interoperability (e.g., Heart Rate Profile, HID over GATT).
    * Profiles are not stored on the device—they are just a specification. Custom profiles are common for proprietary projects.


How Data Transfer Works
-----------------------

**Discovery**: Client performs service/characteristic discovery after connection.

**Operations (via ATT PDUs):**
* Read / Write (with or without response)
* Notifications (server pushes updates when value changes – very efficient)
* Indications (reliable notifications with ACK)
* Long reads/writes (for values > MTU)

**MTU negotiation**: Default 23 bytes; can be increased (up to 512+ bytes in modern stacks) for higher throughput.

GATT makes BLE extremely flexible: you can use standardized SIG services for interoperability or define fully
custom services/characteristics for your application. All modern BLE stacks (Android, iOS, Nordic, TI, ESP32, etc.)
expose GATT APIs for creating or consuming these structures.