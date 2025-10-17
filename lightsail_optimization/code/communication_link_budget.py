#!/usr/bin/env python3
"""
Communication Link Budget Calculator for Warpeed Lightsail Project
α Centauri to Earth Optical Communication Analysis

This module calculates the complete communication link budget for laser
communication from α Centauri (4.37 light-years) back to Earth using
optical frequencies (1550 nm wavelength).

Author: Communication Systems Engineer
Date: 2025-10-15
"""

import numpy as np
import json
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from scipy.constants import c, h, k
import os

# Physical Constants
SPEED_OF_LIGHT = c  # m/s
PLANCK_CONSTANT = h  # J·s
BOLTZMANN_CONSTANT = k  # J/K

class OpticalLinkBudget:
    """
    Calculates optical communication link budget for interstellar communication.
    """

    def __init__(self):
        """Initialize link budget parameters."""

        # Distance Parameters
        self.distance_ly = 4.37  # light-years
        self.distance_km = 4.13e13  # km
        self.distance_m = self.distance_km * 1000  # meters

        # Transmitter Parameters
        self.tx_power_W = 1.0  # 1 Watt laser
        self.wavelength_nm = 1550  # nanometers (telecom wavelength)
        self.wavelength_m = self.wavelength_nm * 1e-9  # meters
        self.frequency_Hz = SPEED_OF_LIGHT / self.wavelength_m  # Hz

        # Transmitter Optics (Lightsail-based transmitter)
        self.tx_aperture_diameter_m = 1.0  # 1m diameter transmitter telescope
        self.tx_aperture_area_m2 = np.pi * (self.tx_aperture_diameter_m / 2)**2
        self.tx_efficiency = 0.7  # Transmitter optical efficiency

        # Receiver Parameters (Earth-based telescope)
        self.rx_aperture_diameter_m = 100.0  # 100m ground telescope
        self.rx_aperture_area_m2 = np.pi * (self.rx_aperture_diameter_m / 2)**2
        self.rx_efficiency = 0.6  # Receiver optical efficiency

        # Atmospheric Parameters
        self.atmospheric_transmission = 0.7  # 70% transmission (good conditions)
        self.zenith_angle_deg = 30  # degrees from zenith
        self.airmass = 1 / np.cos(np.radians(self.zenith_angle_deg))

        # Detector Parameters
        self.detector_quantum_efficiency = 0.8  # 80% QE for InGaAs detector
        self.detector_dark_current = 1e-12  # A (very low for cooled detector)
        self.detector_temperature_K = 200  # Cooled detector temperature
        self.detector_bandwidth_Hz = 1e9  # 1 GHz bandwidth

        # Background Noise Sources
        self.sky_brightness_mag_arcsec2 = 22  # V-band magnitude/arcsec²
        self.zodiacal_light_photons_s_m2_nm = 1e6  # photons/s/m²/nm

        # Data Parameters
        self.image_width_px = 1024
        self.image_height_px = 1024
        self.bits_per_pixel = 16
        self.total_bits_per_image = self.image_width_px * self.image_height_px * self.bits_per_pixel

        # Required Performance
        self.required_SNR_dB = 10  # Minimum SNR for reliable communication
        self.required_SNR_linear = 10**(self.required_SNR_dB / 10)

        # Results storage
        self.results = {}

    def calculate_beam_divergence(self):
        """
        Calculate laser beam divergence angle and beam diameter at receiver.
        Uses diffraction-limited beam divergence formula.

        Returns:
            dict: Beam divergence parameters
        """
        # Diffraction-limited beam divergence (half-angle)
        # θ = 1.22 * λ / D
        theta_rad = 1.22 * self.wavelength_m / self.tx_aperture_diameter_m
        theta_urad = theta_rad * 1e6  # microradians

        # Beam diameter at receiver distance
        beam_radius_m = self.distance_m * theta_rad
        beam_diameter_m = 2 * beam_radius_m
        beam_diameter_km = beam_diameter_m / 1000

        # Beam area at receiver
        beam_area_m2 = np.pi * beam_radius_m**2

        print(f"\n{'='*70}")
        print(f"BEAM DIVERGENCE ANALYSIS")
        print(f"{'='*70}")
        print(f"Transmitter aperture diameter: {self.tx_aperture_diameter_m:.2f} m")
        print(f"Wavelength: {self.wavelength_nm:.0f} nm")
        print(f"Beam divergence half-angle: {theta_urad:.3f} μrad")
        print(f"Beam diameter at {self.distance_ly:.2f} ly: {beam_diameter_km:.2e} km")
        print(f"Beam diameter at receiver: {beam_diameter_m:.2e} m")
        print(f"Beam area at receiver: {beam_area_m2:.2e} m²")

        return {
            'divergence_rad': theta_rad,
            'divergence_urad': theta_urad,
            'beam_diameter_m': beam_diameter_m,
            'beam_diameter_km': beam_diameter_km,
            'beam_area_m2': beam_area_m2
        }

    def calculate_free_space_path_loss(self):
        """
        Calculate free-space path loss using Friis transmission equation.
        FSPL (dB) = 20*log₁₀(4πd/λ)

        Returns:
            dict: Path loss parameters
        """
        # Free-space path loss (linear)
        fspl_linear = (4 * np.pi * self.distance_m / self.wavelength_m)**2

        # Convert to dB
        fspl_dB = 10 * np.log10(fspl_linear)

        print(f"\n{'='*70}")
        print(f"FREE-SPACE PATH LOSS (FSPL)")
        print(f"{'='*70}")
        print(f"Distance: {self.distance_ly:.2f} light-years = {self.distance_m:.3e} m")
        print(f"Wavelength: {self.wavelength_m:.3e} m ({self.wavelength_nm:.0f} nm)")
        print(f"Path loss: {fspl_dB:.2f} dB")
        print(f"Path loss (linear): {fspl_linear:.3e}")

        return {
            'path_loss_dB': fspl_dB,
            'path_loss_linear': fspl_linear
        }

    def calculate_geometric_spreading_loss(self):
        """
        Calculate power density reduction due to beam spreading.

        Returns:
            dict: Spreading loss parameters
        """
        beam_params = self.calculate_beam_divergence()
        beam_area = beam_params['beam_area_m2']

        # Fraction of beam power captured by receiver
        collection_fraction = self.rx_aperture_area_m2 / beam_area

        # Spreading loss in dB
        spreading_loss_dB = -10 * np.log10(collection_fraction)

        print(f"\n{'='*70}")
        print(f"GEOMETRIC SPREADING LOSS")
        print(f"{'='*70}")
        print(f"Beam area at receiver: {beam_area:.3e} m²")
        print(f"Receiver aperture area: {self.rx_aperture_area_m2:.2f} m²")
        print(f"Collection fraction: {collection_fraction:.3e}")
        print(f"Spreading loss: {spreading_loss_dB:.2f} dB")

        return {
            'beam_area_m2': beam_area,
            'collection_fraction': collection_fraction,
            'spreading_loss_dB': spreading_loss_dB
        }

    def calculate_received_power(self):
        """
        Calculate received optical power at Earth telescope.
        Uses Friis equation: P_rx = P_tx * (λ/(4πd))² * G_tx * G_rx * η

        Returns:
            dict: Received power parameters
        """
        # Antenna gains (for diffraction-limited apertures)
        # G = (πD/λ)² * efficiency
        G_tx = (np.pi * self.tx_aperture_diameter_m / self.wavelength_m)**2 * self.tx_efficiency
        G_rx = (np.pi * self.rx_aperture_diameter_m / self.wavelength_m)**2 * self.rx_efficiency

        # Path loss
        path_loss = self.calculate_free_space_path_loss()
        path_loss_linear = path_loss['path_loss_linear']

        # Received power (before atmosphere)
        P_rx_space = (self.tx_power_W * G_tx * G_rx) / path_loss_linear

        # Apply atmospheric attenuation with airmass correction
        atmospheric_loss = self.atmospheric_transmission ** self.airmass
        P_rx_ground = P_rx_space * atmospheric_loss

        # Convert to dBm
        P_rx_space_dBm = 10 * np.log10(P_rx_space * 1000)  # mW
        P_rx_ground_dBm = 10 * np.log10(P_rx_ground * 1000)  # mW

        # Atmospheric loss in dB
        atmospheric_loss_dB = -10 * np.log10(atmospheric_loss)

        print(f"\n{'='*70}")
        print(f"RECEIVED POWER CALCULATION")
        print(f"{'='*70}")
        print(f"Transmit power: {self.tx_power_W:.2f} W ({10*np.log10(self.tx_power_W*1000):.2f} dBm)")
        print(f"Transmitter gain: {10*np.log10(G_tx):.2f} dBi")
        print(f"Receiver gain: {10*np.log10(G_rx):.2f} dBi")
        print(f"Free-space path loss: {path_loss['path_loss_dB']:.2f} dB")
        print(f"Received power (above atmosphere): {P_rx_space:.3e} W ({P_rx_space_dBm:.2f} dBm)")
        print(f"Atmospheric loss (airmass {self.airmass:.2f}): {atmospheric_loss_dB:.2f} dB")
        print(f"Received power (ground): {P_rx_ground:.3e} W ({P_rx_ground_dBm:.2f} dBm)")

        # Number of photons per second
        photon_energy_J = PLANCK_CONSTANT * self.frequency_Hz
        photons_per_second = P_rx_ground / photon_energy_J

        print(f"Photon energy: {photon_energy_J:.3e} J")
        print(f"Received photons/second: {photons_per_second:.3e}")

        return {
            'tx_gain_dBi': 10 * np.log10(G_tx),
            'rx_gain_dBi': 10 * np.log10(G_rx),
            'received_power_space_W': P_rx_space,
            'received_power_space_dBm': P_rx_space_dBm,
            'atmospheric_loss_dB': atmospheric_loss_dB,
            'received_power_ground_W': P_rx_ground,
            'received_power_ground_dBm': P_rx_ground_dBm,
            'photons_per_second': photons_per_second,
            'photon_energy_J': photon_energy_J
        }

    def calculate_noise_sources(self):
        """
        Calculate all noise sources affecting the receiver:
        - Shot noise from signal
        - Background sky noise (zodiacal light, airglow)
        - Detector dark current noise
        - Thermal noise

        Returns:
            dict: Noise power parameters
        """
        rx_power = self.calculate_received_power()
        P_rx = rx_power['received_power_ground_W']
        photons_per_second = rx_power['photons_per_second']
        photon_energy = rx_power['photon_energy_J']

        # Detected photons per second (with quantum efficiency)
        detected_photons_per_second = photons_per_second * self.detector_quantum_efficiency

        # Shot noise from signal (photon counting statistics)
        # For bandwidth B, shot noise variance = 2*q*I*B where I is photocurrent
        signal_current = detected_photons_per_second * 1.602e-19  # Convert to Amperes
        shot_noise_variance = 2 * 1.602e-19 * signal_current * self.detector_bandwidth_Hz
        shot_noise_current = np.sqrt(shot_noise_variance)

        # Background noise from zodiacal light and sky
        # Approximate as photons collected from sky background
        receiver_solid_angle_sr = (self.wavelength_m / self.rx_aperture_diameter_m)**2

        # Background photon flux per m² per nm per second
        background_photons_per_second = (self.zodiacal_light_photons_s_m2_nm *
                                         self.rx_aperture_area_m2 *
                                         1.0)  # 1 nm spectral width

        background_current = (background_photons_per_second *
                             self.detector_quantum_efficiency *
                             1.602e-19)

        background_shot_noise_variance = 2 * 1.602e-19 * background_current * self.detector_bandwidth_Hz
        background_noise_current = np.sqrt(background_shot_noise_variance)

        # Dark current noise
        dark_current_noise_variance = 2 * 1.602e-19 * self.detector_dark_current * self.detector_bandwidth_Hz
        dark_current_noise = np.sqrt(dark_current_noise_variance)

        # Thermal (Johnson) noise from detector resistance
        # Assume 1 MΩ load resistance
        load_resistance_ohm = 1e6
        thermal_noise_variance = 4 * BOLTZMANN_CONSTANT * self.detector_temperature_K * self.detector_bandwidth_Hz / load_resistance_ohm
        thermal_noise_current = np.sqrt(thermal_noise_variance)

        # Total noise (RMS sum)
        total_noise_current = np.sqrt(shot_noise_variance +
                                     background_shot_noise_variance +
                                     dark_current_noise_variance +
                                     thermal_noise_variance)

        # Noise power
        noise_power_W = total_noise_current**2 * load_resistance_ohm

        print(f"\n{'='*70}")
        print(f"NOISE ANALYSIS")
        print(f"{'='*70}")
        print(f"Signal photons/s: {photons_per_second:.3e}")
        print(f"Detected photons/s (QE={self.detector_quantum_efficiency}): {detected_photons_per_second:.3e}")
        print(f"Signal current: {signal_current:.3e} A")
        print(f"Shot noise current: {shot_noise_current:.3e} A")
        print(f"Background photons/s: {background_photons_per_second:.3e}")
        print(f"Background noise current: {background_noise_current:.3e} A")
        print(f"Dark current: {self.detector_dark_current:.3e} A")
        print(f"Dark current noise: {dark_current_noise:.3e} A")
        print(f"Thermal noise current: {thermal_noise_current:.3e} A")
        print(f"Total noise current: {total_noise_current:.3e} A")
        print(f"Noise power: {noise_power_W:.3e} W")

        return {
            'signal_current_A': signal_current,
            'shot_noise_current_A': shot_noise_current,
            'background_noise_current_A': background_noise_current,
            'dark_current_noise_A': dark_current_noise,
            'thermal_noise_current_A': thermal_noise_current,
            'total_noise_current_A': total_noise_current,
            'noise_power_W': noise_power_W
        }

    def calculate_SNR(self):
        """
        Calculate signal-to-noise ratio.

        Returns:
            dict: SNR parameters
        """
        rx_power = self.calculate_received_power()
        noise = self.calculate_noise_sources()

        signal_power_W = rx_power['received_power_ground_W']
        noise_power_W = noise['noise_power_W']

        # SNR (linear)
        SNR_linear = signal_power_W / noise_power_W

        # SNR (dB)
        SNR_dB = 10 * np.log10(SNR_linear)

        # Link margin
        link_margin_dB = SNR_dB - self.required_SNR_dB

        print(f"\n{'='*70}")
        print(f"SIGNAL-TO-NOISE RATIO (SNR)")
        print(f"{'='*70}")
        print(f"Signal power: {signal_power_W:.3e} W")
        print(f"Noise power: {noise_power_W:.3e} W")
        print(f"SNR: {SNR_dB:.2f} dB (linear: {SNR_linear:.3e})")
        print(f"Required SNR: {self.required_SNR_dB:.2f} dB")
        print(f"Link margin: {link_margin_dB:.2f} dB")

        return {
            'SNR_linear': SNR_linear,
            'SNR_dB': SNR_dB,
            'required_SNR_dB': self.required_SNR_dB,
            'link_margin_dB': link_margin_dB
        }

    def calculate_data_rate(self):
        """
        Calculate achievable data rate using Shannon-Hartley theorem.
        C = B * log₂(1 + SNR)

        Returns:
            dict: Data rate parameters
        """
        snr = self.calculate_SNR()
        SNR_linear = snr['SNR_linear']

        # Shannon capacity
        capacity_bps = self.detector_bandwidth_Hz * np.log2(1 + SNR_linear)

        # Apply coding overhead (assume rate-1/2 FEC coding for robustness)
        coding_rate = 0.5
        effective_data_rate_bps = capacity_bps * coding_rate

        # Time to transmit one image
        time_per_image_seconds = self.total_bits_per_image / effective_data_rate_bps
        time_per_image_hours = time_per_image_seconds / 3600
        time_per_image_days = time_per_image_hours / 24

        # Images per year
        seconds_per_year = 365.25 * 24 * 3600
        images_per_year = seconds_per_year / time_per_image_seconds

        print(f"\n{'='*70}")
        print(f"DATA RATE CALCULATION")
        print(f"{'='*70}")
        print(f"Bandwidth: {self.detector_bandwidth_Hz:.3e} Hz ({self.detector_bandwidth_Hz/1e9:.2f} GHz)")
        print(f"SNR (linear): {SNR_linear:.3e}")
        print(f"Shannon capacity: {capacity_bps:.3e} bps ({capacity_bps/1e6:.3f} Mbps)")
        print(f"Coding rate: {coding_rate:.1f}")
        print(f"Effective data rate: {effective_data_rate_bps:.3e} bps ({effective_data_rate_bps/1e6:.3f} Mbps)")
        print(f"\nImage transmission:")
        print(f"Image size: {self.image_width_px}×{self.image_height_px} pixels, {self.bits_per_pixel} bits/pixel")
        print(f"Total bits per image: {self.total_bits_per_image:.3e} ({self.total_bits_per_image/(8*1024*1024):.2f} MiB)")
        print(f"Time per image: {time_per_image_seconds:.2f} seconds ({time_per_image_hours:.2f} hours / {time_per_image_days:.2f} days)")
        print(f"Images per year: {images_per_year:.2f}")

        return {
            'shannon_capacity_bps': capacity_bps,
            'shannon_capacity_Mbps': capacity_bps / 1e6,
            'coding_rate': coding_rate,
            'data_rate_bps': effective_data_rate_bps,
            'data_rate_Mbps': effective_data_rate_bps / 1e6,
            'bits_per_image': self.total_bits_per_image,
            'time_per_image_seconds': time_per_image_seconds,
            'time_per_image_hours': time_per_image_hours,
            'time_per_image_days': time_per_image_days,
            'images_per_year': images_per_year
        }

    def assess_communication_viability(self):
        """
        Determine if communication link is viable.

        Returns:
            dict: Viability assessment
        """
        snr = self.calculate_SNR()
        data_rate = self.calculate_data_rate()

        # Check if SNR meets requirement
        snr_adequate = snr['SNR_dB'] >= self.required_SNR_dB

        # Check if data rate is practical (> 1 bps)
        data_rate_practical = data_rate['data_rate_bps'] > 1.0

        # Check if image transmission time is reasonable (< 1 year)
        time_reasonable = data_rate['time_per_image_days'] < 365

        # Overall viability
        communication_viable = snr_adequate and data_rate_practical

        print(f"\n{'='*70}")
        print(f"COMMUNICATION VIABILITY ASSESSMENT")
        print(f"{'='*70}")
        print(f"SNR adequate (≥ {self.required_SNR_dB} dB): {snr_adequate} (actual: {snr['SNR_dB']:.2f} dB)")
        print(f"Data rate practical (> 1 bps): {data_rate_practical} (actual: {data_rate['data_rate_bps']:.3e} bps)")
        print(f"Image time reasonable (< 1 year): {time_reasonable} (actual: {data_rate['time_per_image_days']:.2f} days)")
        print(f"\n{'*'*70}")
        print(f"COMMUNICATION VIABLE: {communication_viable}")
        print(f"{'*'*70}")

        if communication_viable:
            print(f"\n✓ The link budget analysis confirms that optical communication")
            print(f"  from α Centauri to Earth is VIABLE with the specified parameters.")
            print(f"  Link margin: {snr['link_margin_dB']:.2f} dB")
            print(f"  Achievable data rate: {data_rate['data_rate_Mbps']:.6f} Mbps")
            print(f"  Time per image: {data_rate['time_per_image_hours']:.2f} hours")
        else:
            print(f"\n✗ The link budget analysis indicates that optical communication")
            print(f"  from α Centauri to Earth is NOT VIABLE with current parameters.")
            print(f"  Consider: larger transmitter, higher power, or larger receiver.")

        return {
            'snr_adequate': snr_adequate,
            'data_rate_practical': data_rate_practical,
            'time_reasonable': time_reasonable,
            'communication_viable': communication_viable
        }

    def generate_link_budget_diagram(self, output_path):
        """
        Generate visual link budget diagram showing power flow.

        Args:
            output_path: Path to save diagram
        """
        # Calculate all parameters
        rx_power = self.calculate_received_power()
        path_loss = self.calculate_free_space_path_loss()
        snr = self.calculate_SNR()
        data_rate = self.calculate_data_rate()

        # Create figure
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

        # ===== Top plot: Power flow diagram =====
        ax1.axis('off')
        ax1.set_xlim(0, 10)
        ax1.set_ylim(0, 8)

        # Title
        ax1.text(5, 7.5, 'Optical Communication Link Budget',
                ha='center', fontsize=16, fontweight='bold')
        ax1.text(5, 7.0, 'α Centauri → Earth (4.37 light-years)',
                ha='center', fontsize=12, style='italic')

        # Transmitter box
        tx_box = FancyBboxPatch((0.5, 5), 1.5, 1.2, boxstyle="round,pad=0.1",
                                edgecolor='blue', facecolor='lightblue', linewidth=2)
        ax1.add_patch(tx_box)
        ax1.text(1.25, 6.2, 'Transmitter', ha='center', fontsize=10, fontweight='bold')
        ax1.text(1.25, 5.8, f'{self.tx_power_W:.1f} W', ha='center', fontsize=9)
        ax1.text(1.25, 5.5, f'{self.wavelength_nm:.0f} nm', ha='center', fontsize=9)
        ax1.text(1.25, 5.2, f'D={self.tx_aperture_diameter_m:.1f}m', ha='center', fontsize=8)

        # Free space path
        arrow1 = FancyArrowPatch((2.0, 5.6), (4.5, 5.6),
                                arrowstyle='->', mutation_scale=20, linewidth=2, color='red')
        ax1.add_patch(arrow1)
        ax1.text(3.25, 6.1, 'Free Space', ha='center', fontsize=9)
        ax1.text(3.25, 5.9, f'Loss: {path_loss["path_loss_dB"]:.1f} dB', ha='center', fontsize=9)

        # Space receiver power
        space_box = FancyBboxPatch((4.5, 5), 1.5, 1.2, boxstyle="round,pad=0.1",
                                  edgecolor='purple', facecolor='lavender', linewidth=2)
        ax1.add_patch(space_box)
        ax1.text(5.25, 6.2, 'Above Atm', ha='center', fontsize=10, fontweight='bold')
        ax1.text(5.25, 5.7, f'{rx_power["received_power_space_dBm"]:.1f}', ha='center', fontsize=9)
        ax1.text(5.25, 5.4, 'dBm', ha='center', fontsize=9)
        ax1.text(5.25, 5.1, f'{rx_power["received_power_space_W"]:.2e} W', ha='center', fontsize=7)

        # Atmospheric attenuation
        arrow2 = FancyArrowPatch((6.0, 5.6), (7.5, 5.6),
                                arrowstyle='->', mutation_scale=20, linewidth=2, color='orange')
        ax1.add_patch(arrow2)
        ax1.text(6.75, 6.1, 'Atmosphere', ha='center', fontsize=9)
        ax1.text(6.75, 5.9, f'Loss: {rx_power["atmospheric_loss_dB"]:.1f} dB', ha='center', fontsize=9)

        # Receiver box
        rx_box = FancyBboxPatch((7.5, 5), 2, 1.2, boxstyle="round,pad=0.1",
                               edgecolor='green', facecolor='lightgreen', linewidth=2)
        ax1.add_patch(rx_box)
        ax1.text(8.5, 6.2, 'Receiver', ha='center', fontsize=10, fontweight='bold')
        ax1.text(8.5, 5.7, f'{rx_power["received_power_ground_dBm"]:.1f} dBm', ha='center', fontsize=9)
        ax1.text(8.5, 5.4, f'{rx_power["received_power_ground_W"]:.2e} W', ha='center', fontsize=8)
        ax1.text(8.5, 5.1, f'D={self.rx_aperture_diameter_m:.0f}m', ha='center', fontsize=8)

        # Link budget table
        table_data = [
            ['Parameter', 'Value'],
            ['Distance', f'{self.distance_ly:.2f} ly'],
            ['Path Loss', f'{path_loss["path_loss_dB"]:.1f} dB'],
            ['Tx Power', f'{10*np.log10(self.tx_power_W*1000):.1f} dBm'],
            ['Tx Gain', f'{rx_power["tx_gain_dBi"]:.1f} dBi'],
            ['Rx Gain', f'{rx_power["rx_gain_dBi"]:.1f} dBi'],
            ['Atm Loss', f'{rx_power["atmospheric_loss_dB"]:.1f} dB'],
            ['Rx Power', f'{rx_power["received_power_ground_dBm"]:.1f} dBm'],
            ['SNR', f'{snr["SNR_dB"]:.2f} dB'],
            ['Link Margin', f'{snr["link_margin_dB"]:.2f} dB'],
        ]

        table = ax1.table(cellText=table_data, cellLoc='left',
                         bbox=[0.5, 0.5, 3, 3.5], edges='closed')
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.2)

        # Style header row
        for i in range(2):
            table[(0, i)].set_facecolor('lightgray')
            table[(0, i)].set_text_props(weight='bold')

        # Data rate info
        info_data = [
            ['Performance', 'Value'],
            ['Data Rate', f'{data_rate["data_rate_Mbps"]:.6f} Mbps'],
            ['Image Size', f'{self.total_bits_per_image/(8*1024*1024):.2f} MiB'],
            ['Time/Image', f'{data_rate["time_per_image_hours"]:.2f} hrs'],
            ['Images/Year', f'{data_rate["images_per_year"]:.1f}'],
            ['Viable?', 'YES' if self.assess_communication_viability()['communication_viable'] else 'NO'],
        ]

        table2 = ax1.table(cellText=info_data, cellLoc='left',
                          bbox=[5.5, 0.5, 4, 3.5], edges='closed')
        table2.auto_set_font_size(False)
        table2.set_fontsize(9)
        table2.scale(1, 1.2)

        for i in range(2):
            table2[(0, i)].set_facecolor('lightgray')
            table2[(0, i)].set_text_props(weight='bold')

        # Color-code viability
        viability = self.assess_communication_viability()['communication_viable']
        table2[(5, 1)].set_facecolor('lightgreen' if viability else 'lightcoral')
        table2[(5, 1)].set_text_props(weight='bold')

        # ===== Bottom plot: Link budget bar chart =====
        categories = ['Tx\nPower', 'Tx\nGain', 'Free Space\nPath Loss',
                     'Rx\nGain', 'Atmospheric\nLoss', 'Rx\nPower', 'Noise', 'SNR']
        values = [
            10*np.log10(self.tx_power_W*1000),  # dBm
            rx_power["tx_gain_dBi"],
            -path_loss["path_loss_dB"],
            rx_power["rx_gain_dBi"],
            -rx_power["atmospheric_loss_dB"],
            rx_power["received_power_ground_dBm"],
            10*np.log10(self.calculate_noise_sources()['noise_power_W']*1000),  # dBm
            snr["SNR_dB"]
        ]

        colors = ['blue', 'cyan', 'red', 'cyan', 'orange', 'green', 'purple', 'gold']

        bars = ax2.bar(categories, values, color=colors, alpha=0.7, edgecolor='black')
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax2.set_ylabel('Power Level (dB relative to 1mW)', fontsize=11, fontweight='bold')
        ax2.set_title('Link Budget Components', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')

        # Add value labels on bars
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{val:.1f}', ha='center', va='bottom' if val > 0 else 'top',
                    fontsize=9, fontweight='bold')

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"\n{'='*70}")
        print(f"Link budget diagram saved to: {output_path}")
        print(f"{'='*70}")

        plt.close()

    def run_complete_analysis(self, output_dir):
        """
        Run complete link budget analysis and save results.

        Args:
            output_dir: Directory to save output files
        """
        print("\n" + "="*70)
        print("WARPEED LIGHTSAIL COMMUNICATION LINK BUDGET ANALYSIS")
        print("α Centauri → Earth Optical Communication")
        print("="*70)

        # Run all calculations
        beam_div = self.calculate_beam_divergence()
        path_loss = self.calculate_free_space_path_loss()
        spreading = self.calculate_geometric_spreading_loss()
        rx_power = self.calculate_received_power()
        noise = self.calculate_noise_sources()
        snr = self.calculate_SNR()
        data_rate = self.calculate_data_rate()
        viability = self.assess_communication_viability()

        # Compile results
        results = {
            'mission_parameters': {
                'distance_light_years': self.distance_ly,
                'distance_km': self.distance_km,
                'wavelength_nm': self.wavelength_nm,
                'transmitter_power_W': self.tx_power_W,
                'transmitter_diameter_m': self.tx_aperture_diameter_m,
                'receiver_diameter_m': self.rx_aperture_diameter_m,
            },
            'beam_divergence': {
                'divergence_urad': beam_div['divergence_urad'],
                'beam_diameter_at_earth_km': beam_div['beam_diameter_km'],
                'beam_area_m2': beam_div['beam_area_m2'],
            },
            'link_budget': {
                'path_loss_dB': path_loss['path_loss_dB'],
                'spreading_loss_dB': spreading['spreading_loss_dB'],
                'tx_gain_dBi': rx_power['tx_gain_dBi'],
                'rx_gain_dBi': rx_power['rx_gain_dBi'],
                'atmospheric_loss_dB': rx_power['atmospheric_loss_dB'],
                'received_power_W': rx_power['received_power_ground_W'],
                'received_power_dBm': rx_power['received_power_ground_dBm'],
                'photons_per_second': rx_power['photons_per_second'],
            },
            'noise_analysis': {
                'signal_current_A': noise['signal_current_A'],
                'total_noise_current_A': noise['total_noise_current_A'],
                'noise_power_W': noise['noise_power_W'],
            },
            'performance': {
                'SNR_dB': snr['SNR_dB'],
                'required_SNR_dB': snr['required_SNR_dB'],
                'link_margin_dB': snr['link_margin_dB'],
                'data_rate_bps': data_rate['data_rate_bps'],
                'data_rate_Mbps': data_rate['data_rate_Mbps'],
                'shannon_capacity_Mbps': data_rate['shannon_capacity_Mbps'],
            },
            'image_transmission': {
                'bits_per_image': data_rate['bits_per_image'],
                'time_per_image_hours': data_rate['time_per_image_hours'],
                'time_per_image_days': data_rate['time_per_image_days'],
                'images_per_year': data_rate['images_per_year'],
            },
            'viability_assessment': {
                'communication_viable': bool(viability['communication_viable']),
                'snr_adequate': bool(viability['snr_adequate']),
                'data_rate_practical': bool(viability['data_rate_practical']),
                'time_reasonable': bool(viability['time_reasonable']),
            }
        }

        # Convert numpy types to native Python types for JSON serialization
        def convert_numpy_types(obj):
            if isinstance(obj, dict):
                return {k: convert_numpy_types(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [convert_numpy_types(v) for v in obj]
            elif isinstance(obj, (np.integer, np.floating, np.bool_)):
                return obj.item()
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return obj

        results = convert_numpy_types(results)

        # Save JSON results
        os.makedirs(output_dir, exist_ok=True)
        json_path = os.path.join(output_dir, 'communication_link_results.json')
        with open(json_path, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\nResults saved to: {json_path}")

        # Generate diagram
        diagram_path = os.path.join(output_dir, 'communication_link_budget.png')
        self.generate_link_budget_diagram(diagram_path)

        return results


def main():
    """Main execution function."""

    # Initialize link budget calculator
    link_budget = OpticalLinkBudget()

    # Run complete analysis
    output_dir = '/Users/heinzjungbluth/Desktop/Warp/lightsail_optimization/results'
    results = link_budget.run_complete_analysis(output_dir)

    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print(f"\nKey Results:")
    print(f"  - Communication Viable: {results['viability_assessment']['communication_viable']}")
    print(f"  - SNR: {results['performance']['SNR_dB']:.2f} dB")
    print(f"  - Link Margin: {results['performance']['link_margin_dB']:.2f} dB")
    print(f"  - Data Rate: {results['performance']['data_rate_Mbps']:.6f} Mbps")
    print(f"  - Time per Image: {results['image_transmission']['time_per_image_hours']:.2f} hours")
    print(f"  - Images per Year: {results['image_transmission']['images_per_year']:.1f}")

    return results


if __name__ == "__main__":
    main()
