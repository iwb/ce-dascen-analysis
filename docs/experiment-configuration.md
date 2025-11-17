# Experiment Configuration
This document outlines the configuration used in the application use case and details the design of experiments (DOE), input data, attribute specifications, and calculation methods.


> **🔬 Research software notice**: This document is part of a research prototype (v2025.11) and serves as implementation guidance. Scientific references are included for contextual understanding and further reading only. The peer-reviewed scientific contribution can only be found in the published article.


## Table of Contents

- [1. Use Case Description](#1-use-case-description)
  - [1.1 Product](#11-product)
  - [1.2 Process](#12-process)
  - [1.3 Resource](#13-resource)
  - [1.4 System](#14-system)
- [2. Configuration & Calculations](#2-configuration--calculations)
  - [2.1 Performance Indicators](#21-performance-indicators)
  - [2.2 Analysis Groups](#22-analysis-groups)
  - [2.3 Value Calculations](#23-value-calculations)
- [3. Experimental Design (DOE)](#3-experimental-design-doe)
  - [3.2 Production Scheduling Configuration](#32-production-scheduling-configuration)
  - [3.3 Automation Level Specifications](#33-automation-level-specifications)
  - [3.4 System Configurations](#34-system-configurations)
  - [3.5 Product Portfolio Definitions](#35-product-portfolio-definitions)
- [References](#references)

<br>

---

<br>

<!-- ================================================== -->
<!-- USE CASE -->
<!-- ================================================== -->
## 1. Use Case Description
The use case is based on data that was collected at the Smart Production Lab (SPL) at the Institute for Machine Tools and Industrial Management (*iwb*) at the Technical University of Munich (https://iwb-spl.de/). The dataset comprises six disassembly scenarios with 60 remotely controlled electric buggies and 240+ component extractions. It was scaled in order to approximate real-world disassembly operations. The disassembly scenario learning factory dataset (DASCEN-LF) is available at https://github.com/iwb/ce-dascen-lf-data.

> **⚠️ Methodological note:** The data scaling approach has limitations. However, the objective of this use case is to demonstrate the applicability of the framework, not to provide generalizable insights into disassembly operations.

### 1.1 Product
Tables 1.1 show the weight of each component across the four vehicle types *HD* (hail damage), *TL* (total loss), *SA* (shock absorber defect), and *RD* (rear damage).

<br>

**Table 1.1.** Component codes and component-specific attributes (Source: [`data/attributes/attributes_product.json`](../data/attributes/attributes_product.json))

<table>
  <thead>
    <tr>
      <th width="9%" rowspan="2">Code</th>
      <th width="15%" rowspan="2">Component</th>
      <th width="4%" rowspan="2">HD</th>
      <th width="4%" rowspan="2">TL</th>
      <th width="4%" rowspan="2">SA</th>
      <th width="4%" rowspan="2">RD</th>
      <th colspan="3">Original data<sup>[1]</sup></th>
      <th colspan="1">Exp. config.</th>
    </tr>
    <tr>
      <th width="6%">Quantity</th>
      <th width="9%">Weight (g)</th>
      <th width="9%">Share of total weight (%)<sup>[2]</sup></th>
      <th width="12%">Weight (kg)<sup>[3]</sup></th>
    </tr>
  </thead>
  <tbody>
    <tr><td><strong>car</strong></td><td colspan="5" style="text-align: center;"><em>Incoming end-of-life vehicle</em></td><td>1</td><td>1360</td><td>100</td><td>762<sup>[5]</sup></td></tr>
    <tr><td><strong>BOSP</strong></td><td>Body & Spoiler</td><td>✓</td><td>✓</td><td>-</td><td>✓</td><td>1+1</td><td>77</td><td>5.7</td><td>43.4</td></tr>
    <tr><td><strong>BAT</strong></td><td>Battery</td><td>✓</td><td>✓</td><td>-</td><td>-</td><td>1</td><td>396</td><td>29.1</td><td>221.7</td></tr>
    <tr><td><strong>RT</strong></td><td>Rear tires</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>2</td><td>142</td><td>10.4</td><td>79.2</td></tr>
    <tr><td><strong>FT</strong></td><td>Front tires</td><td>✓</td><td>✓</td><td>✓</td><td>-</td><td>2</td><td>97</td><td>7.1</td><td>54.1</td></tr>
    <tr><td><strong>FAXS</strong></td><td>Front axis with shock absorbers</td><td>✓</td><td>-</td><td>-</td><td>-</td><td>1</td><td>155</td><td>11.4</td><td>86.9</td></tr>
    <tr><td><strong>SSA</strong></td><td>Small shock absorbers</td><td>✓</td><td>-</td><td>✓</td><td>-</td><td>2</td><td>15</td><td>1.1</td><td>8.4</td></tr>
    <tr><td><strong>FAX</strong></td><td>Front Axis</td><td>✓</td><td>-</td><td>-</td><td>-</td><td>1</td><td>140</td><td>10.3</td><td>78.5</td></tr>
    <tr><td><strong>CHS</strong></td><td>Chassis</td><td>✓</td><td>-</td><td>-</td><td>-</td><td>1</td><td>414</td><td>30.4</td><td>231.6</td></tr>
    <tr><td><strong>CORE</strong></td><td>Chassis with systems and engine</td><td>-</td><td>-</td><td>-</td><td>✓</td><td>1</td><td>600</td><td>44.1</td><td>336.0</td></tr>
    <tr><td><strong>BSA</strong></td><td>Big shock absorbers</td><td>✓</td><td>-</td><td>✓</td><td>✓</td><td>2</td><td>15</td><td>1.1</td><td>8.4</td></tr>
    <tr><td><strong>RAX</strong></td><td>Rear Axis</td><td>✓</td><td>-</td><td>-</td><td>✓</td><td>1</td><td>500</td><td>36.8</td><td>280.4</td></tr>
    <tr><td><strong>CRE</strong></td><td>Chassis, remaining systems, engine</td><td>-</td><td>✓</td><td>-</td><td>-</td><td>1</td><td>648</td><td>47.6</td><td>362.7</td></tr>
    <tr><td><strong>CSEB-NABS</strong></td><td>Chassis, systems, engine, body</td><td>-</td><td>-</td><td>✓</td><td>-</td><td>1</td><td>1090</td><td>80.1</td><td>610.4</td></tr>
  </tbody>
</table>

<details>
<summary>Table notes</summary>

- [1] Original data: extracted from the DASCEN-LF dataset <a href="#jordan-et-al-2024">(Jordan et al. 2024)</a>
- [2] Share of total weight: percentage relative to total vehicle weight (1360 g per car)
- [3] Weight (kg): component weights were scaled based on percentage values relative to a reference buggy weight (762 kg)
- [4] Assembly naming: FAXS (Front Axis with Shock Absorbers) appears in simulation event logs as FRONT_AXIS_GROUP. Similarly, intermediate rear axis assemblies appear as REAR_AXIS_GROUP. These represent assembly groups that are subsequently disassembled into individual components (e.g., SSA and FAX from FRONT_AXIS_GROUP).
- [5] Reference buggy weight: 762 kg
- ✓ = Component present in vehicle type, - = Component not present

</details>

<br>

---

<br>

Table 1.2 shows the quality-dependent recovery options and values.

<br>

**Table 1.2.** Quality-dependent component recovery configurations (Source: [`data/attributes/attributes_product.json`](../data/attributes/attributes_product.json))

<table>
  <thead>
    <tr>
      <th width="6%" rowspan="2">Code</th>
      <th colspan="1">Original data<sup>[1]</sup></th>
      <th colspan="6">Exp. config.</th>
    </tr>
    <tr>
      <th width="8%">Value (EUR)</th>
      <th width="8%">Value (EUR)<sup>[2]</sup></th>
      <th width="10%">Type<sup>[3]</sup></th>
      <th width="10%">Quality range<sup>[4]</sup></th>
      <th width="9%">Value factor<sup>[5]</sup></th>
      <th width="9%">Value (EUR)<sup>[6]</sup></th>
      <th width="12%">EOL circularity factor<sup>[7]</sup></th>
    </tr>
  </thead>
  <tbody>
    <tr><td><strong>car</strong></td><td>230</td><td>40,000<sup>[9]</sup></td><td colspan="5" style="text-align: center;"><em>Incoming end-of-life vehicle</em></td></tr>
    <tr><td><strong>BOSP</strong></td><td>44</td><td>7,652</td><td>Recycling</td><td>0.0-1.0</td><td>0.1</td><td>765</td><td>0.29</td></tr>
    <tr><td rowspan="3"><strong>BAT</strong></td><td rowspan="3">42</td><td rowspan="3">7,304</td><td>Reuse</td><td>1.0</td><td>0.5</td><td>3,652</td><td>1.0</td></tr>
    <tr><td>Reman</td><td>0.8-0.99</td><td>0.25</td><td>1,826</td><td>0.57</td></tr>
    <tr><td>Recycling</td><td>0.0-0.79</td><td>0.1</td><td>730</td><td>0.29</td></tr>
    <tr><td rowspan="3"><strong>RT</strong></td><td rowspan="3">26</td><td rowspan="3">4,522</td><td>Reuse</td><td>1.0</td><td>0.5</td><td>2,261</td><td>1.0</td></tr>
    <tr><td>Reman</td><td>0.8-0.99</td><td>0.25</td><td>1,131</td><td>0.57</td></tr>
    <tr><td>Recycling</td><td>0.0-0.79</td><td>0.1</td><td>452</td><td>0.29</td></tr>
    <tr><td rowspan="3"><strong>FT</strong></td><td rowspan="3">24</td><td rowspan="3">4,174</td><td>Reuse</td><td>1.0</td><td>0.5</td><td>2,087</td><td>1.0</td></tr>
    <tr><td>Reman</td><td>0.8-0.99</td><td>0.25</td><td>1,044</td><td>0.57</td></tr>
    <tr><td>Recycling</td><td>0.0-0.79</td><td>0.1</td><td>417</td><td>0.29</td></tr>
    <tr><td rowspan="3"><strong>FAXS</strong></td><td rowspan="3">50</td><td rowspan="3">8,696</td><td>Reuse</td><td>1.0</td><td>0.5</td><td>4,348</td><td>1.0</td></tr>
    <tr><td>Reman</td><td>0.8-0.99</td><td>0.25</td><td>2,174</td><td>0.57</td></tr>
    <tr><td>Recycling</td><td>0.0-0.79</td><td>0.1</td><td>870</td><td>0.29</td></tr>
    <tr><td><strong>SSA</strong></td><td>21</td><td>3,652</td><td>Recycling</td><td>0.0-1.0</td><td>0.1</td><td>365</td><td>0.29</td></tr>
    <tr><td rowspan="2"><strong>FAX</strong></td><td rowspan="2">30</td><td rowspan="2">5,217</td><td>Reman</td><td>0.8-1.0</td><td>0.25</td><td>1,304</td><td>0.57</td></tr>
    <tr><td>Recycling</td><td>0.0-0.79</td><td>0.1</td><td>522</td><td>0.29</td></tr>
    <tr><td rowspan="3"><strong>CHS</strong></td><td rowspan="3">56</td><td rowspan="3">9,739</td><td>Reuse</td><td>1.0</td><td>0.5</td><td>4,870</td><td>1.0</td></tr>
    <tr><td>Reman</td><td>0.8-0.99</td><td>0.25</td><td>2,435</td><td>0.57</td></tr>
    <tr><td>Recycling</td><td>0.0-0.79</td><td>0.1</td><td>974</td><td>0.29</td></tr>
    <tr><td rowspan="3"><strong>CORE</strong></td><td rowspan="3">110</td><td rowspan="3">19,130</td><td>Reuse</td><td>1.0</td><td>0.5</td><td>9,565</td><td>1.0</td></tr>
    <tr><td>Reman</td><td>0.8-0.99</td><td>0.25</td><td>4,783</td><td>0.57</td></tr>
    <tr><td>Recycling</td><td>0.0-0.79</td><td>0.1</td><td>1,913</td><td>0.29</td></tr>
    <tr><td rowspan="2"><strong>BSA</strong></td><td rowspan="2">21</td><td rowspan="2">3,652</td><td>Reman</td><td>0.8-1.0</td><td>0.25</td><td>913</td><td>0.57</td></tr>
    <tr><td>Recycling</td><td>0.0-0.79</td><td>0.1</td><td>365</td><td>0.29</td></tr>
    <tr><td><strong>RAX</strong></td><td>50</td><td>8,696</td><td>Recycling</td><td>0.0-1.0</td><td>0.1</td><td>870</td><td>0.29</td></tr>
    <tr><td><strong>CRE</strong></td><td>94</td><td>16,348</td><td>Recycling</td><td>0.0-1.0</td><td>0.1</td><td>1,635</td><td>0.29</td></tr>
    <tr><td><strong>CSEB-NABS</strong></td><td>138</td><td>24,000</td><td>Recycling</td><td>0.0-1.0</td><td>0.1</td><td>2,400</td><td>0.29</td></tr>
  </tbody>
</table>

<details>
<summary>Table notes</summary>

- [1] Original data: extracted from the DASCEN-LF dataset <a href="#jordan-et-al-2024">(Jordan et al. 2024)</a>
- [2] Value (EUR): the component values were scaled based on the relative value to a reference buggy value (40,000 Euro total value)
- [3] Type: end-of-life recovery strategy based on defined destinations in the DASCEN-LF dataset <a href="#jordan-et-al-2024">(Jordan et al. 2024)</a>
- [4] Quality range: component condition score determining the applicable recovery option (0.0 = worst, 1.0 = perfect); current implementation: all components were simulated with a quality of 1.0.
- [5] Value factor: multiplier applied to base value based on recovery type (0.1 = Recycling, 0.25 = Reman, 0.5 = Reuse)
- [6] Value (EUR): calculated component recovery value (Base Value × Value Factor)
- [7] EOL circularity factor: circularity rating based on the 9R framework by <a href="#potting-et-al-2016">Potting et al. (2016)</a>, setting Reuse (R3) as the preferred level (7/7) and Recover (R9) as the least preferred option (1/7), resulting in (Recycling = 2/7 = 0.29; Remanufacturing = 4/7 = 0.57, Reuse = 7/7 = 1.0)
- [9] Total vehicle value: 40,000 Euro

</details>

<br>

---

<br>

### 1.2 Process

Table 1.3 presents the process step times for the eight disassembly operations (S1 to S8). The process times vary based on the tool type (manual vs. automated) and represent the active processing duration for the component extraction.

<br>

**Table 1.3.** Process step times and outputs (Source: [`experiment_data/config/product_config/`](../experiment_data/config/product_config/))

<table>
  <thead>
    <tr>
      <th width="7%" rowspan="2">Step</th>
      <th width="11%" rowspan="2">Operation</th>
      <th width="19%" rowspan="2">Output</th>
      <th width="9%" rowspan="2">Tool</th>
      <th colspan="1">Original data<sup>[1]</sup></th>
      <th colspan="2">Exp. config.<sup>[2]</sup></th>
    </tr>
    <tr>
      <th width="12%">Time (sec)</th>
      <th width="10%">Factor</th>
      <th width="12%">Value (min)</th>
    </tr>
  </thead>
  <tbody>
    <tr><td><strong>S1</strong></td><td>BOSP</td><td>BOSP (body & spoiler)</td><td>Manual</td><td>53</td><td>10</td><td>8.83</td></tr>
    <tr><td><strong>S2</strong></td><td>BAT</td><td>BAT (battery)</td><td>Manual</td><td>42</td><td>10</td><td>7.00</td></tr>
    <tr><td rowspan="2"><strong>S3</strong></td><td rowspan="2">RT</td><td rowspan="2">RT (rear tires)</td><td>Manual</td><td>67</td><td>10</td><td>11.17</td></tr>
    <tr><td>Auto</td><td>59</td><td>10</td><td>9.83</td></tr>
    <tr><td rowspan="2"><strong>S4</strong></td><td rowspan="2">FT</td><td rowspan="2">FT (front tires)</td><td>Manual</td><td>75</td><td>10</td><td>12.50</td></tr>
    <tr><td>Auto</td><td>36</td><td>10</td><td>6.00</td></tr>
    <tr><td rowspan="2"><strong>S5</strong></td><td rowspan="2">FAXS</td><td rowspan="2">FAXS (front axis with SSA)<sup>[3]</sup></td><td>Manual</td><td>141</td><td>10</td><td>23.50</td></tr>
    <tr><td>Auto</td><td>97</td><td>10</td><td>16.17</td></tr>
    <tr><td rowspan="2"><strong>S6</strong></td><td rowspan="2">SSA</td><td rowspan="2">SSA (small shock absorbers)</td><td>Manual</td><td>131</td><td>10</td><td>21.83</td></tr>
    <tr><td>Auto</td><td>83</td><td>10</td><td>13.83</td></tr>
    <tr><td rowspan="2"><strong>S7</strong></td><td rowspan="2">CHS/CORE</td><td rowspan="2">CHS (chassis) or CORE<sup>[4]</sup></td><td>Manual</td><td>125</td><td>10</td><td>20.83</td></tr>
    <tr><td>Auto</td><td>78</td><td>10</td><td>13.00</td></tr>
    <tr><td rowspan="2"><strong>S8</strong></td><td rowspan="2">BSA</td><td rowspan="2">BSA (big shock sbsorbers)<sup>[5]</sup></td><td>Manual</td><td>99</td><td>10</td><td>16.50</td></tr>
    <tr><td>Auto</td><td>83</td><td>10</td><td>13.83</td></tr>
  </tbody>
</table>

<details>
<summary>Table notes</summary>

- <sup>[1]</sup> Original data: mean disassembly times (cleaned) from DASCEN-LF dataset
- <sup>[2]</sup> Experimental configuration: Complexity-adjusted scaling for real-world vehicle operations
- <sup>[3]</sup> FAXS separates into SSA and FAX in subsequent operations; also releases REAR_AXIS_GROUP (passive)
- <sup>[4]</sup> CHS for car_hd, CORE for car_rd
- <sup>[5]</sup> Also releases passive remainder assembly: RAX_HD (car_hd), CSEB-NABS (car_sa), or RAX_RD (car_rd)
- Manual = hand tools, Auto = cordless screwdriver
- Process times represent the active disassembly duration, excluding the time for material handling and transport

</details>

<br>

---

<br>

**Table 1.4.** Disassembly path structure by vehicle type (Source: [`data/attributes/attributes_disassembly_paths.json`](../data/attributes/attributes_disassembly_paths.json))

<table>
  <thead>
    <tr>
      <th width="5%">ID<sup>[1]</sup></th>
      <th width="8%">Code<sup>[2]</sup></th>
      <th width="12%">Name</th>
      <th width="8%"># Steps</th>
      <th width="20%">Process steps<sup>[3]</sup></th>
      <th width="13%"># Components</th>
      <th width="34%">Components<sup>[4]</sup></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>HD</strong></td>
      <td>car_hd</td>
      <td>Hail damage</td>
      <td>8</td>
      <td>S1→S2→S3→S4→S5→[S6, S7→S8]</td>
      <td>14</td>
      <td>BOSP (1+1), BAT, RT (2×), FT (2×), SSA (2×), FAX, CHS, BSA (2×), RAX_HD</td>
    </tr>
    <tr>
      <td><strong>TL</strong></td>
      <td>car_tl</td>
      <td>Total loss</td>
      <td>4</td>
      <td>S1→S2→S3→S4</td>
      <td>8</td>
      <td>BOSP (1+1), BAT, RT (2×), FT (2×), CRE</td>
    </tr>
    <tr>
      <td><strong>SA</strong></td>
      <td>car_sa</td>
      <td>Shock absorber</td>
      <td>4</td>
      <td>S3→S4→S6→S8</td>
      <td>9</td>
      <td>RT (2×), FT (2×), SSA (2×), BSA (2×), CSEB-NABS</td>
    </tr>
    <tr>
      <td><strong>RD</strong></td>
      <td>car_rd</td>
      <td>Rear damage</td>
      <td>4</td>
      <td>S1→S3→S7→S8</td>
      <td>8</td>
      <td>BOSP (1+1), RT (2×), CORE, BSA (2×), RAX_RD</td>
    </tr>
  </tbody>
</table>

<details>
<summary>Table notes</summary>

- <sup>[1]</sup> ID: notation used in the publication (HD, TL, SA, RD)
- <sup>[2]</sup> Code: dataset nomenclature (car_hd, car_tl, car_sa, car_rd) used in configuration files and experimental data
- <sup>[3]</sup> Process steps: for car_hd, step S5 splits into parallel branches: front_axis (S6: SSA, FAX) and rear_axis (S7→S8: CHS, BSA)
- <sup>[4]</sup> Components: includes passive components (RAX_HD, CRE, CSEB-NABS, RAX_RD) that are released during the final disassembly step without separate operation (process time ≤ 0.5 sec), tracked for material flow

</details>

<br>

---

<br>

### 1.3 Resource
The resource attributes shown in table 1.5 define the labor costs, energy consumption, and fixed operational costs for workstations.

<br>

**Table 1.5.** Resource attribute specifications (Source: [`data/attributes/attributes_resource.json`](../data/attributes/attributes_resource.json))

<table>
  <thead>
    <tr>
      <th width="50%">Attribute</th>
      <th width="18%">Manual</th>
      <th width="18%">Automated</th>
      <th width="14%">Unit</th>
    </tr>
  </thead>
  <tbody>
    <tr><td><strong>Labor rate<sup>[1]</sup></strong></td><td>66</td><td>66</td><td>EUR/h</td></tr>
    <tr><td><strong>Power rating<sup>[2]</sup></strong></td><td>0</td><td>0.5</td><td>kW</td></tr>
    <tr><td><strong>Fixed costs<sup>[3]</sup></strong></td><td>21</td><td>21</td><td>EUR/h</td></tr>
  </tbody>
</table>

<details>
<summary>Table Notes</summary>

- <sup>[1]</sup> Labor rate: reflects the productive hour costs accounting for non-productive time. While standard hourly wages range from 20-38 EUR/h, productive hour rates reach 50-90 EUR/h assuming 34% productivity efficiency <a href="#zimmermann-et-al-2022">(Zimmermann et al. 2022)</a>. The selected rate of 66 EUR/h represents the mid-range productive hour costs.
- <sup>[2]</sup> Power rating: based on the specifications of an industrial cordless impact wrench (Bosch GDS 18V-1050 H: 18V, 5Ah battery, 1050 Nm torque). The power draw of 0.5 kW was estimated for these specifications.
- <sup>[3]</sup> Fixed costs: include investments, depreciation, insurance, taxes, system costs, and administrative activities. Based on 85 EUR/ELV fixed costs for 500 ELVs/year operations <a href="#zimmermann-et-al-2022">(Zimmermann et al. 2022)</a>, allocated for an assumed 2,000 operating hours annually, this yields 21.25 EUR/h (85 × 500 / 2,000). 

</details>

<br>

---

<br>

### 1.4 System
Table 1.6 shows the defined system-level parameters.

<br>

**Table 1.6.** System-level attributes (Source: [`data/attributes/attributes_system.json`](../data/attributes/attributes_system.json))

<table>
  <thead>
    <tr>
      <th width="60%">Attribute</th>
      <th width="20%">Value</th>
      <th width="20%">Unit</th>
    </tr>
  </thead>
  <tbody>
    <tr><td><strong>Energy rate<sup>[1]</sup></strong></td><td>0.4</td><td>EUR/kWh</td></tr>
    <tr><td><strong>System fixed costs<sup>[2]</sup></strong></td><td>0</td><td>EUR</td></tr>
  </tbody>
</table>

<details>
<summary>Table notes</summary>

- <sup>[1]</sup> Energy rate: reflects the German household electricity prices for small-scale operations consuming less than 3,500 kWh annually. The rate of 0.40 EUR/kWh is based on the current German household tariffs <a href="#bdew-2025">(BDEW 2025)</a>. Industrial rates (0.18 EUR/kWh) apply only to operations exceeding 160,000 kWh annual consumption.
- <sup>[2]</sup> System fixed costs: set to 0 EUR to isolate operational effects in experimental comparison.

</details>

<br>

---

<!-- ================================================== -->
<!-- INDICATORS -->
<!-- ================================================== -->

<br>

## 2. Configuration & Calculations

### 2.1 Indicators and Values

The in table 2.1 listed six performance indicators were defined following the selection method as outlined in <a href="indicator_selection.md">indicator_selection.md</a>.

<br>

**Table 2.1.** Performance indicator definitions and parameters (Source: [`config/config_indicators.json`](../data/config/config_indicators.json))

<table>
  <thead>
    <tr>
      <th width="8%">ID</th>
      <th width="18%">Name</th>
      <th width="25%">Formula</th>
      <th width="7%">Unit</th>
      <th width="8%">Weight<sup>[1]</sup></th>
      <th width="10%">Threshold</th>
      <th width="10%">Direction</th>
      <th width="14%">Category</th>
    </tr>
  </thead>
  <tbody>
    <tr><td><strong>IND01</strong></td><td>Electricity Consumption</td><td><code>process_duration/60 × power_rating</code></td><td>kWh</td><td>0.166</td><td>45,000</td><td>minimize</td><td>Environmental</td></tr>
    <tr><td><strong>IND02</strong></td><td>Utilization Rate</td><td><code>runtime_minutes / factory_open_time_minutes × 100</code></td><td>%</td><td>0.166</td><td>50</td><td>maximize</td><td>Economic</td></tr>
    <tr><td><strong>IND03</strong></td><td>Labor Cost</td><td><code>process_duration/60 × labor_rate</code></td><td>EUR</td><td>0.166</td><td>18,000</td><td>minimize</td><td>Economic</td></tr>
    <tr><td><strong>IND04</strong></td><td>Lead Time</td><td><code>lead_time</code><sup>[2]</sup></td><td>minutes</td><td>0.166</td><td>13,100</td><td>minimize</td><td>Economic</td></tr>
    <tr><td><strong>IND05</strong></td><td>Production Output</td><td><code>component_value</code><sup>[3]</sup></td><td>EUR</td><td>0.166</td><td>6,000</td><td>maximize</td><td>Economic</td></tr>
    <tr><td><strong>IND06</strong></td><td>Circularity Index</td><td><code>component_weight × circularity_rating</code></td><td>kg</td><td>0.166</td><td>400</td><td>maximize</td><td>Environmental</td></tr>
  </tbody>
</table>

<details>
<summary>Table notes</summary>

- <sup>[1]</sup> Weight distribution: equal weighting (1/6 = 0.166 per indicator) ensures balanced consideration of economic and environmental objectives without subjective prioritization. Total weight = 1.0 (normalized scoring).
- <sup>[2]</sup> Lead time: calculated per product
- <sup>[3]</sup> Production output: quality-based component value

</details>

<br>

Table 2.2 lists the supporting value calculations required to calculate, for example, the disassembly depth profits.

**Table 2.2.** Value calculation formulas (Source: [`config/config_values.json`](../data/config/config_values.json))

<table>
  <thead>
    <tr>
      <th width="10%">ID</th>
      <th width="15%">Name</th>
      <th width="25%">Formula</th>
      <th width="7%">Unit</th>
      <th width="13%">Category<sup>[1]</sup></th>
      <th width="30%">Usage</th>
    </tr>
  </thead>
  <tbody>
    <tr><td><strong>VAL01</strong></td><td>Labor cost</td><td><code>process_duration/60 × labor_rate</code></td><td>EUR</td><td>Cost factor</td><td>Component-level labor cost (same as IND03)</td></tr>
    <tr><td><strong>VAL02</strong></td><td>Fixed cost</td><td><code>process_duration/60 × fixed_cost_per_hour</code></td><td>EUR</td><td>Cost factor</td><td>Component-level equipment cost</td></tr>
    <tr><td><strong>VAL03</strong></td><td>Electricity cost</td><td><code>IND01 × energy_rate</code></td><td>EUR</td><td>Cost factor</td><td>Component-level energy cost</td></tr>
    <tr><td><strong>VAL04</strong></td><td>System baseline cost</td><td><code>system_fixed_cost</code></td><td>EUR</td><td>Cost factor</td><td>System-level fixed investment</td></tr>
    <tr><td><strong>REVENUE</strong></td><td>Revenue</td><td><code>IND05</code></td><td>EUR</td><td>Aggregate</td><td>Component recovery value (from IND05)</td></tr>
    <tr><td><strong>COSTS_FIX</strong></td><td>Fixed costs</td><td><code>VAL02</code></td><td>EUR</td><td>Aggregate</td><td>Total fixed costs</td></tr>
    <tr><td><strong>COSTS_VAR</strong></td><td>Variable costs</td><td><code>VAL01 + VAL03</code></td><td>EUR</td><td>Aggregate</td><td>Total variable costs<sup>[2]</sup></td></tr>
    <tr><td><strong>PROFIT</strong></td><td>Profit</td><td><code>REVENUE - COSTS_FIX - COSTS_VAR</code></td><td>EUR</td><td>Aggregate</td><td>Net profit per experiment<sup>[3]</sup></td></tr>
  </tbody>
</table>

<details>
<summary>Table notes</summary>

- <sup>[1]</sup> Cost structure categories: cost factors are individual cost components, aggregates are combined cost calculations
- <sup>[2]</sup> Variable costs: Labor (VAL01) + Electricity (VAL03) - scale with production volume
- <sup>[3]</sup> Profitability: PROFIT = component revenue minus all cost categories; fixed costs include equipment time allocation (VAL02) + system setup (VAL04) - constant per experiment

</details>


<br>

---

<br>

### 2.2 Analysis Groups
Table 2.3 shows the seven implemented groups that enable the statistical aggregation across experimental factors.

<br>

**Table 2.3.** Analysis group definitions (Source: [`config/config_groups.json`](../data/config/config_groups.json))

<table>
  <thead>
    <tr>
      <th width="8%">ID</th>
      <th width="15%">Grouped by</th>
      <th width="12%">Feature group(s)<sup>[1]</sup></th>
      <th width="10%">Type</th>
      <th width="18%">Grouping variables</th>
      <th width="17%">Levels</th>
      <th width="20%">Purpose</th>
    </tr>
  </thead>
  <tbody>
    <tr><td><strong>G01</strong></td><td>System</td><td>S03</td><td>Single</td><td>system</td><td>4 (01, 02, 03, 05)</td><td>Compare system configurations</td></tr>
    <tr><td><strong>G02</strong></td><td>Product portfolio</td><td>P05, S19</td><td>Single</td><td>product_mix</td><td>6 (hd, tl, sa, rd, balanced, mixed, sa_rd)</td><td>Analyze portfolio effects</td></tr>
    <tr><td><strong>G03</strong></td><td>Automation degree</td><td>S09</td><td>Single</td><td>automation_degree → automation_level</td><td>4 (manual 0.0, low 0.01-0.33, medium 0.34-0.66, high 0.67-1.0)</td><td>Assess automation impact</td></tr>
    <tr><td><strong>G05</strong></td><td>Division type</td><td>S01</td><td>Single</td><td>division_type</td><td>2 (labor, quantity)</td><td>Compare division strategies</td></tr>
    <tr><td><strong>G06</strong></td><td>Number of workstations</td><td>S04</td><td>Single</td><td>num_stations</td><td>3 (3, 4, 5 stations)</td><td>Evaluate station count effect</td></tr>
    <tr><td><strong>G11</strong></td><td>Product portfolio and system</td><td>S03×P05</td><td>Interaction</td><td>product_mix, system</td><td>20 (5 mixes × 4 systems)</td><td>Identify portfolio-system synergies</td></tr>
    <tr><td><strong>G12</strong></td><td>Type, automation degree, and number of workstations</td><td>S11×S09×S04</td><td>Interaction</td><td>system_type, automation_level, num_stations</td><td>~18 combinations</td><td>Multi-factor interaction analysis</td></tr>
  </tbody>
</table>

<details>
<summary>Table notes</summary>

- <sup>[1]</sup> Feature group IDs reference to the classification described in ([feature-groups.md](feature-groups.md)). P = Product-related groups, S = System-related groups.

</details>

<br>




---

<!-- ================================================== -->
<!-- DOE -->
<!-- ================================================== -->

<br>

## 3. Experimental Design (DOE)
The experimental design follows a full factorial design using three factors: system configurations, product portfolios, and automation levels. As shown in table 3.1, this results in 96 experiments.

**Table 3.1.** Factorial design overview (Source: [`experiment_data/doe/doe_full_factorial_experiments.csv`](../experiment_data/doe/doe_full_factorial_experiments.csv))

<table>
  <thead>
    <tr>
      <th width="20%">Factor</th>
      <th width="10%">Levels</th>
      <th width="35%">Values</th>
      <th width="35%">Description</th>
    </tr>
  </thead>
  <tbody>
    <tr><td><strong>Systems</strong></td><td>4</td><td>system_01, system_02, system_03, system_05</td><td>Different layouts and division strategies</td></tr>
    <tr><td><strong>Portfolios</strong></td><td>6</td><td>portfolio_1 through portfolio_6</td><td>Various product portfolio scenarios</td></tr>
    <tr><td><strong>Automation</strong></td><td>4</td><td>manual, front, critical, full</td><td>Strategic automation levels</td></tr>
    <tr><td><strong>Total Experiments</strong></td><td>96</td><td>4 × 6 × 4 = 96</td><td>Full factorial design</td></tr>
  </tbody>
</table>

Each experiment references to one system configuration file ([`experiment_data/config/system_config/`](../experiment_data/config/system_config/)), one scheduling file ([`experiment_data/config/delivery_schedules/`](../experiment_data/config/delivery_schedules/)), and multiple product configuration files ([`experiment_data/config/product_config/`](../experiment_data/config/product_config/)). The experimental design is documented in [`experiment_data/doe/doe_full_factorial_experiments.csv`](../experiment_data/doe/doe_full_factorial_experiments.csv).

All experiments use the in table 3.2. outlined scheduling parameters to enable the comparability across different disassembly scenarios. The production schedule simulates a one-week operation period.

**Table 3.2.** Production scheduling configuration

<table>
  <thead>
    <tr>
      <th width="25%">Parameter</th>
      <th width="15%">Value</th>
      <th width="15%">Unit</th>
      <th width="45%">Description</th>
    </tr>
  </thead>
  <tbody>
    <tr><td><strong>Total volume</strong></td><td>40</td><td>cars</td><td>Total vehicles per experiment</td></tr>
    <tr><td><strong>Simulation duration</strong></td><td>7</td><td>days</td><td>One working week</td></tr>
    <tr><td><strong>Working hours</strong></td><td>7:00-17:00</td><td>time</td><td>10-hour shifts</td></tr>
    <tr><td><strong>Interarrival time</strong><sup>[1]</sup></td><td>Variable</td><td>minutes</td><td>Time between consecutive deliveries</td></tr>
    <tr><td><strong>Delivery pattern</strong><sup>[2]</sup></td><td>Sequential</td><td>-</td><td>Delivery schedule based on portfolio composition</td></tr>
  </tbody>
</table>

<details>
<summary>Table notes</summary>

- <sup>[1]</sup> Interarrival time: time between consecutive vehicle deliveries
- <sup>[2]</sup> Delivery pattern: sequential delivery of a total of 40 vehicles over one week

</details>

<br>

---

<br>

### 3.1 Portfolio Definitions
There are six product portfolios that represent different end-of-life vehicle return scenarios, ranging from balanced distributions to specialized processing focuses (see table 3.3). Each portfolio contains 40 vehicles and varies in composition by damage type. The scheduling configurations are defined in files following the pattern `sch_{portfolio}_{automation}.json`, where `{automation}` represents the automation level code (a00, a02, a04, or a06).

**Table 3.3.** Product portfolio specifications (Source: [`experiment_data/config/delivery_schedules/`](../experiment_data/config/delivery_schedules/))

<table>
  <thead>
    <tr>
      <th width="5%">ID<sup>[1]</sup></th>
      <th width="10%">Portfolio<sup>[2]</sup></th>
      <th width="5%">HD</th>
      <th width="5%">TL</th>
      <th width="5%">SA</th>
      <th width="5%">RD</th>
      <th width="8%">Total Cars</th>
      <th width="10%"># Components</th>
      <th width="22%">Description</th>
      <th width="25%">Configured in</th>
    </tr>
  </thead>
  <tbody>
    <tr><td><strong>P1</strong></td><td>portfolio_1</td><td>10</td><td>10</td><td>10</td><td>10</td><td>40</td><td>390</td><td>Balanced mix - equal distribution</td><td><code>sch_balanced_{auto}.json</code><sup>[3]</sup></td></tr>
    <tr><td><strong>P2</strong></td><td>portfolio_2</td><td>25</td><td>15</td><td>0</td><td>0</td><td>40</td><td>470</td><td>Front damage focus</td><td><code>sch_front_{auto}.json</code></td></tr>
    <tr><td><strong>P3</strong></td><td>portfolio_3</td><td>0</td><td>0</td><td>20</td><td>20</td><td>40</td><td>340</td><td>Rear focus only</td><td><code>sch_rear_{auto}.json</code></td></tr>
    <tr><td><strong>P4</strong></td><td>portfolio_4</td><td>40</td><td>0</td><td>0</td><td>0</td><td>40</td><td>560</td><td>HD specialization</td><td><code>sch_hd_{auto}.json</code></td></tr>
    <tr><td><strong>P5</strong></td><td>portfolio_5</td><td>0</td><td>15</td><td>15</td><td>10</td><td>40</td><td>335</td><td>Mixed without HD</td><td><code>sch_mixed_{auto}.json</code></td></tr>
    <tr><td><strong>P6</strong></td><td>portfolio_6</td><td>5</td><td>5</td><td>20</td><td>10</td><td>40</td><td>370</td><td>SA/RD heavy mix</td><td><code>sch_sa_rd_{auto}.json</code></td></tr>
  </tbody>
</table>

<details>
<summary>Table notes</summary>

- <sup>[1]</sup> ID: notation used in the publication
- <sup>[2]</sup> Portfolio: dataset nomenclature (portfolio_1 through portfolio_6) used in configuration files and experimental data
- <sup>[3]</sup> `{auto}` represents the automation level code: a00 (manual), a02 (tires), a04 (critical), or a06 (full)
- HD = Hail Damage (14 components/car), TL = Total Loss (8 components/car)
- SA = Shock Absorber defects (9 components/car), RD = Rear Damage (8 components/car)

</details>

<br>

---

<br>

### 3.2 System Configurations
Table 3.4 shows the four disassembly system configurations that represent different approaches to organizing material flow and work division. The systems vary by layout type (line versus workshop), division strategy (labor versus quantity), and number of workstations. Each system is defined in a configuration file `system_{number}.json`. This file specifies the layout, workstation assignments, and material flow logic.

**Table 3.4.** System configuration specifications (Source: [`experiment_data/config/system_config/`](../experiment_data/config/system_config/))

<table>
  <thead>
    <tr>
      <th width="5%">ID<sup>[1]</sup></th>
      <th width="5%">System<sup>[2]</sup></th>
      <th width="5%">Layout</th>
      <th width="5%">Division</th>
      <th width="5%">Stations</th>
      <th width="30%">Workstation Assignment<sup>[3]</sup></th>
      <th width="10%">Configured in</th>
    </tr>
  </thead>
  <tbody>
    <tr><td><strong>S1</strong></td><td>system_01</td><td>Line</td><td>Labor</td><td>3</td><td>ws-03 (S1 to S4), ws-04 (S5, S7), ws-05 (S6, S8)</td><td><code>system_01.json</code></td></tr>
    <tr><td><strong>S2</strong></td><td>system_02</td><td>Workshop</td><td>Quantity</td><td>4</td><td>ws-01 through ws-04 (S1 to S8)</td><td><code>system_02.json</code></td></tr>
    <tr><td><strong>S3</strong></td><td>system_03</td><td>Line</td><td>Labor</td><td>5</td><td>ws-01 (S1, S2), ws-02 (S3, S4), ws-03 (S5), ws-04 (S7), ws-05 (S6,S8)</td><td><code>system_03.json</code></td></tr>
    <tr><td><strong>S4</strong></td><td>system_05</td><td>Workshop</td><td>Quantity</td><td>5</td><td>ws-01 through ws-05 (S1 to S8)</td><td><code>system_05.json</code></td></tr>
  </tbody>
</table>

<details>
<summary>Table notes</summary>

- <sup>[1]</sup> ID: notation used in the publication (S1-S4)
- <sup>[2]</sup> System: dataset nomenclature (system_01, system_02, system_03, system_05) used in configuration files and experimental data. Note: system_04 and system_06 were used in the experimental design
- <sup>[3]</sup> S1-S8 refer to disassembly steps: S1 (BOSP), S2 (BAT), S3 (RT), S4 (FT), S5 (FAXS), S6 (SSA), S7 (CHS/CORE), S8 (BSA)
- Layout: Line = sequential material flow; Workshop = flexible routing between stations
- Division: Labor = tasks assigned by work content balance; Quantity = complete operations per station

</details>

<br>

---

<br>

### 3.3 Automation Levels
There are four automation levels that represent strategic approaches to automating disassembly operations, ranging from a fully manual baseline to complete automation (see table 3.5). Each level targets different operational priorities, such as labor reduction, high-frequency operations, and critical value recovery. Product-specific automation configurations are defined in files following the pattern `car_{type}_{automation}_{steps}.json`, specifying which disassembly steps use automated tools for each vehicle type.

**Table 3.5.** Automation level specifications (Source: [`experiment_data/config/product_config/`](../experiment_data/config/product_config/))

<table>
  <thead>
    <tr>
      <th width="5%">ID<sup>[1]</sup></th>
      <th width="8%">Level<sup>[2]</sup></th>
      <th width="8%">S1: BOSP</th>
      <th width="8%">S2: BAT</th>
      <th width="8%">S3: RT</th>
      <th width="8%">S4: FT</th>
      <th width="8%">S5: FAXS</th>
      <th width="8%">S6: SSA</th>
      <th width="8%">S7: CHS</th>
      <th width="8%">S8: BSA</th>
      <th width="18%">Description</th>
      <th width="7%">Code<sup>[3]</sup></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>A1</strong></td>
      <td>manual</td>
      <td>M<br>8.83 min</td>
      <td>M<br>7.00 min</td>
      <td>M<br>11.17 min</td>
      <td>M<br>12.50 min</td>
      <td>M<br>23.50 min</td>
      <td>M<br>21.83 min</td>
      <td>M<br>20.83 min</td>
      <td>M<br>16.50 min</td>
      <td>Baseline - hand tools only</td>
      <td><code>a00</code></td>
    </tr>
    <tr>
      <td><strong>A2</strong></td>
      <td>tires</td>
      <td>M<br>8.83 min</td>
      <td>M<br>7.00 min</td>
      <td>A<br>9.83 min</td>
      <td>A<br>6.00 min</td>
      <td>M<br>23.50 min</td>
      <td>M<br>21.83 min</td>
      <td>M<br>20.83 min</td>
      <td>M<br>16.50 min</td>
      <td>Tire automation (high frequency)</td>
      <td><code>a02</code></td>
    </tr>
    <tr>
      <td><strong>A3</strong></td>
      <td>critical</td>
      <td>M<br>8.83 min</td>
      <td>M<br>7.00 min</td>
      <td>A<br>9.83 min</td>
      <td>A<br>6.00 min</td>
      <td>M<br>23.50 min</td>
      <td>A<br>13.83 min</td>
      <td>M<br>20.83 min</td>
      <td>A<br>13.83 min</td>
      <td>Critical steps (tires + shock absorbers)</td>
      <td><code>a04</code></td>
    </tr>
    <tr>
      <td><strong>A4</strong></td>
      <td>full</td>
      <td>M<br>8.83 min</td>
      <td>M<br>7.00 min</td>
      <td>A<br>9.83 min</td>
      <td>A<br>6.00 min</td>
      <td>A<br>16.17 min</td>
      <td>A<br>13.83 min</td>
      <td>A<br>13.00 min</td>
      <td>A<br>13.83 min</td>
      <td>Complete automation</td>
      <td><code>a06</code></td>
    </tr>
  </tbody>
</table>

<details>
<summary>Table notes</summary>

- <sup>[1]</sup> ID: notation used in the publication (A1 to A4)
- <sup>[2]</sup> Level: dataset nomenclature (manual, tires, critical, full) used in configuration
- <sup>[3]</sup> Code format: `a{count}` where count indicates the number of automated steps (a00 = 0 steps, a02 = 2 steps, a04 = 4 steps, a06 = 6 steps)
- **M** = Manual (hand tools), **A** = Automated (powered tools)
- Times shown are process durations in minutes
- S1 and S2 are manual-only operations; automation applies to S3-S8 depending on level

</details>

<br>

---

<!-- ================================================== -->
<!-- REFERENCES -->
<!-- ================================================== -->

<br>

## References

#### Jordan et al. 2024
Jordan, P., Streibel, L., Lindholm, N., Maroof, W., Vernim, S., Goebel, L. and Zaeh, M.F., 2025. Demonstrator-based implementation of an infrastructure for event data acquisition in disassembly material flows. Procedia CIRP, 134, pp.277-282. https://doi.org/10.1016/j.procir.2025.03.040 <br>
GitHub Repository: https://github.com/iwb/ce-dascen-lf-data

#### Potting et al. 2016
Potting, J., Hekkert, M., Worrell, E. and Hanemaaijer, A., Circular Economy: Measuring innovation in product chains. PBL Netherlands Environmental Assessment Agency, PBL Netherlands Assess. Agency, Hague. (2016)

#### Zimmermann et al. 2022
Zimmermann, T., Sander, K., Memelink, R., Knode, M., Freier, M., Porsch, L., Schomerus, T., Wilkes, S. and Flormann, P., 2022. Illegal Treatment of End-of-Life Vehicles: Assessment of the environmental, micro-and macroeconomic effects. German Environment Agency (Umweltbundesamt), Dessau‑Roßlau.

#### BDEW 2025
BDEW Bundesverband der Energie- und Wasserwirtschaft e.V., 2025. BDEW-Strompreisanalyse Januar 2025 [BDEW Electricity Price Analysis January 2025]. Available at: https://www.bdew.de/service/daten-und-grafiken/bdew-strompreisanalyse/ (Accessed: November 2025).