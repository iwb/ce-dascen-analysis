# Feature Groups to Support the Solution Space Exploration
![Status](https://img.shields.io/badge/status-literature%20based-orange)

This document presents an overview of possible feature groups derived from the literature to support the analysis of the solution space in disassembly planning experiments. The classification organizes the feature groups into product-related (P) and system-related (S) groups.


> **🔬 Research software notice**: This document is part of a research prototype (v2025.11) and serves as implementation guidance. Scientific references are included for contextual understanding and further reading only. The peer-reviewed scientific contribution can only be found in the published article.
>
> This list is based on a literature review and represents theoretical grouping concepts related to tactical disassembly planning. The groups and levels presented:
> - have **not been validated by industry experts**,
> - are intended to **support users in defining use-case specific groups** matching their planning context, and
> - are **not exhaustive** (other grouping approaches may be equally valid).


## Table of Contents

- [1. Usage and Notes](#1-usage-and-notes)
- [2. Product-Related Groups](#2-product-related-groups)
  - [2.1 Product Structure and Design](#21-product-structure-and-design)
  - [2.2 Disassembly Aspects](#22-disassembly-aspects)
  - [2.3 Physical Properties](#23-physical-properties)
  - [2.4 Market Environment](#24-market-environment)
- [3. System-Related Groups](#3-system-related-groups)
  - [3.1 System Structure and Organization](#31-system-structure-and-organization)
  - [3.2 Workflow Design](#32-workflow-design)
  - [3.3 Material Flow and Logistics](#33-material-flow-and-logistics)
  - [3.4 Strategy](#34-strategy)
  - [3.5 External Factors](#35-external-factors)

<br>

---

<br>

## 1. Usage and Notes
This classification framework consists of feature groups identified through a systematic literature review. The groups and their descriptions are derived from academic publications to support the exploration of tactical disassembly planning solution space.

**Intention:**<br>
This framework is designed to be a supporting tool, not a prescriptive taxonomy. The feature groups presented here:
- represent one possible categorization synthesized from literature,
- are intended to support researchers and practitioners in developing context-specific groupings,
- should be viewed as starting points for exploration rather than definitive categories, and
- may be complemented by alternative grouping approaches that are equally valid.

**Guidelines**:<br>
The *description column* in each table provides some information to support the understanding, but please refer to the cited references for more comprehensive information. The *Levels column*, when populated:
- shows example categorizations from the listed literature source/s,
- represents one approach,
- may vary significantly across different sources and contexts, and
- should be adapted based on the specific application domain.

**The 7±2 Principle:**<br>
In cases where specific level definitions could not be extracted, the **"7±2" principle** is listed. This principle suggests that humans can effectively process approximately seven (plus or minus two) categories [(Miller 1995)](#miller-1995).

**Practical Application**:<br>
1. Select contextually relevant groups: Not all groups apply to every disassembly scenario. Groups should be selected based on, e.g., specific research questions, available data, and planning objectives.
2. Consider interdependencies: Factors can interact. Groups can be designed with multiple group-dimensions to capture these relationships.
3. Adapt and extend freely: The groups and levels shown are examples from the literature. Levels and groups should be modified, combined, or created to match the specific domain requirements.


---

<br>

## 2. Product-Related Groups

### 2.1 Product Structure and Design
Table 2.1 presents feature groups directly related to the structural composition of a product. These aspects are highly relevant as they directly influence the disassembly effort and processing complexity.

**Table 2.1.** Product structure and design feature groups

<table>
  <thead>
    <tr>
      <th width="2%" style="text-align:center">ID</th>
      <th width="8%">Group</th>
      <th width="20%">Definition</th>
      <th width="5%" style="text-align:center"># Levels</th>
      <th width="15%">Levels</th>
      <th width="45%">Description</th>
      <th width="5%">Based on</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="center"><strong>P01</strong></td>
      <td><strong>Product structure type</strong></td>
      <td>Number of predecessors and successors of individual components or assemblies in the product structure tree</td>
      <td align="center">4</td>
      <td>• Linear<br>• Converging<br>• Diverging<br>• General</td>
      <td>Products with a linear structure have a maximum of one predecessor. Products with a converging structure consist of several individual parts. Diverging product structures mean that individual parts have multiple successors. The quality and productivity of disassembling complex products tends to be lower.</td>
      <td><a href="#stammen-hegener-2002">Stammen-Hegener (2002)</a></td>
    </tr>
    <tr>
      <td align="center"><strong>P02</strong></td>
      <td><strong>Product architecture</strong></td>
      <td>Relationship between the functional and the physical independence of components</td>
      <td align="center">4</td>
      <td>• Integral<br>• Functional – modular<br>• Physical – modular<br>• Modular</td>
      <td>The product architecture determines how easily components can be separated. Modular product architectures are easier to disassemble than integral designs.</td>
      <td><a href="#plötner-2017">Plötner (2017)</a>, <a href="#göpfert-1998">Göpfert (1998)</a></td>
    </tr>
    <tr>
      <td align="center"><strong>P03</strong></td>
      <td><strong>Connection types</strong></td>
      <td>Technique used to join the components of a product together</td>
      <td align="center">3</td>
      <td>• Force-fit<br>• Form-fit<br>• Material-bonded</td>
      <td>The type of connection determines whether components can be separated in a non-destructive way, such as force or form closure, or in a destructive way, such as material closure. This influences tool requirements and value creation potential.</td>
      <td><a href="#scheller-1998">Scheller (1998)</a></td>
    </tr>
  </tbody>
</table>

<br>

---

<br>

### 2.2 Disassembly Aspects
Table 2.2 presents feature groups at the portfolio and product levels that influence the disassembly process. One such factor is the variability of products within a portfolio.

**Table 2.2.** Disassembly aspect feature groups

<table>
  <thead>
    <tr>
      <th width="2%" style="text-align:center">ID</th>
      <th width="8%">Group</th>
      <th width="20%">Definition</th>
      <th width="5%" style="text-align:center"># Levels</th>
      <th width="15%">Levels</th>
      <th width="45%">Description</th>
      <th width="5%">Based on</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="center"><strong>P04</strong></td>
      <td><strong>Disassembly depth</strong></td>
      <td>Scope of disassembly at the end of the product life cycle</td>
      <td align="center">7±2</td>
      <td>-</td>
      <td>The disassembly depth is one of the most important factors in disassembly. In addition to economic and environmental aspects of an individual product, it also influences the performance of the disassembly system.</td>
      <td><a href="#giudice-2010">Giudice (2010)</a>, <a href="#jordan-et-al-2024">Jordan et al. (2024)</a></td>
    </tr>
    <tr>
      <td align="center"><strong>P05</strong></td>
      <td><strong>Variability</strong></td>
      <td>Range and differences within the spectrum of used products delivered</td>
      <td align="center">4</td>
      <td>• Customer-specified products<br>• Standardized products with custom variants<br>• Standardized products with variants<br>• Standardized products without variants</td>
      <td>Disassembling customer-specific old products complicates the process because a large number of different variants must be disassembled.</td>
      <td><a href="#huber-2001">Huber (2001)</a></td>
    </tr>
    <tr>
      <td align="center"><strong>P06</strong></td>
      <td><strong>Resource demand</strong></td>
      <td>Demand for strategically important raw materials that can be recovered from old products</td>
      <td align="center">7±2</td>
      <td>-</td>
      <td>The targeted extraction of critical raw materials can provide additional economic incentives. These materials include, for example, lithium, cobalt, nickel, and manganese.</td>
      <td><a href="#lespant-2021">Lespant (2021)</a>, <a href="#fritz-et-al-2023">Fritz et al. (2023)</a></td>
    </tr>
    <tr>
      <td align="center"><strong>P07</strong></td>
      <td><strong>Product condition</strong></td>
      <td>Physical and functional condition of a product at the time of disassembly</td>
      <td align="center">7±2</td>
      <td>-</td>
      <td>The condition of the product is one of the most important factors in disassembly planning. Products in better condition can be more easily repaired or remanufactured rather than being sent directly for material recycling.</td>
      <td><a href="#ullerich-buscher-2013">Ullerich & Buscher (2013)</a></td>
    </tr>
    <tr>
      <td align="center"><strong>P08</strong></td>
      <td><strong>Disassembly complexity</strong></td>
      <td>Complexity of disassembly (# of components, interfaces, design)</td>
      <td align="center">7±2</td>
      <td>-</td>
      <td>Disassembly complexity is one of the most relevant factors in the disassembly process. The number of components, their interfaces, and the design of the components influence the disassembly complexity.</td>
      <td><a href="#kim-ki-moon-2017">Kim & Ki Moon (2017)</a></td>
    </tr>
    <tr>
      <td align="center"><strong>P09</strong></td>
      <td><strong>Point in product lifecycle</strong></td>
      <td>Phase in which a product is being returned for disassembly</td>
      <td align="center">3</td>
      <td>• Zone 1 (Early failures)<br>• Zone 2 (Random failures)<br>• Zone 3 (Wear-out failures)</td>
      <td>The bathtub curve can be used to classify the type of failure.Zone 1 covers early failures, which are often due to production errors. Zone 2 represents random failures, regardless of duration of use. Zone 3 includes age-related wear or material fatigue at the end of the service life.</td>
      <td><a href="#rieker-2018">Rieker (2018)</a></td>
    </tr>
  </tbody>
</table>

<br>

### 2.3 Physical Properties

Table 2.3 presents feature groups representing the physical characteristics of products and components. These properties influence factors such as the handling requirements, process complexity, and recyclability.

**Table 2.3.** Physical property feature groups

<table>
  <thead>
    <tr>
      <th width="2%" style="text-align:center">ID</th>
      <th width="8%">Group</th>
      <th width="20%">Definition</th>
      <th width="5%" style="text-align:center"># Levels</th>
      <th width="15%">Levels</th>
      <th width="45%">Description</th>
      <th width="5%">Based on</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="center"><strong>P10</strong></td>
      <td><strong>Product size</strong></td>
      <td>Physical dimensions of a product (length, width, height, volume)</td>
      <td align="center">7±2</td>
      <td>-</td>
      <td>As product sizes decrease, conventional standard assembly processes become unsuitable and require specialized precision and micro-assembly techniques. This correlation can be applied to the disassembly process.</td>
      <td><a href="#greitmann-1998">Greitmann (1998)</a></td>
    </tr>
    <tr>
      <td align="center"><strong>P11</strong></td>
      <td><strong>Product weight</strong></td>
      <td>Mass of a product</td>
      <td align="center">7±2</td>
      <td>-</td>
      <td>The product weight is a critical physical property that impacts how products are handled during the disassembly process. The use of lightweight materials facilitates disassembly and enhances the recyclability of products.</td>
      <td><a href="#poschmann-et-al-2020">Poschmann et al. (2020)</a>, <a href="#bayerisches-landesamt-für-umwelt-2022">Bayerisches Landesamt für Umwelt (2022)</a></td>
    </tr>
    <tr>
      <td align="center"><strong>P12</strong></td>
      <td><strong>Hazardous materials</strong></td>
      <td>Materials whose release poses a risk to human health or causes environmental pollution</td>
      <td align="center">7±2</td>
      <td>-</td>
      <td>Due to their hazardous potential, hazardous substances require special treatment and must be considered separately. The properties of these materials can influence the choice of disassembly depth and the disassembly system used.</td>
      <td><a href="#kalaycilar-et-al-2024">Kalaycilar et al. (2024)</a>, <a href="#ohlendorf-2006">Ohlendorf (2006)</a></td>
    </tr>
    <tr>
      <td align="center"><strong>P13</strong></td>
      <td><strong>Material type</strong></td>
      <td>Classification of a product or components according to their basic chemical and physical structures</td>
      <td align="center">4</td>
      <td>• Metals<br>• Plastics<br>• Ceramics and Glass<br>• Composites</td>
      <td>Each type of material has different disassembly characteristics. Ceramics and glass, for example, might require a different handling process compared to metals, as they are more brittle, which increases the risk of a brittle fracture.</td>
      <td><a href="#callister-rethwisch-2018">Callister & Rethwisch (2018)</a></td>
    </tr>
    <tr>
      <td align="center"><strong>P14</strong></td>
      <td><strong>Material diversity</strong></td>
      <td>Number of different materials used in a product</td>
      <td align="center">7±2</td>
      <td>-</td>
      <td>A large number of different materials distributed throughout the product makes recycling difficult. The clear separability of materials is essential for efficient recycling, which can influence the need for disassembly and sorting steps.</td>
      <td><a href="#huber-2001">Huber (2001)</a></td>
    </tr>
  </tbody>
</table>

<br>

### 2.4 Market Environment

Table 2.4 presents feature groups that represent the market context in which products are distributed and used. The model of the five competitive forces [(Porter 1998)](#porter-1998) was used to identify the relevant feature classes. These groups cover three of the forces.

**Table 2.4.** Market environment feature groups

<table>
  <thead>
    <tr>
      <th width="2%" style="text-align:center">ID</th>
      <th width="8%">Group</th>
      <th width="20%">Definition</th>
      <th width="5%" style="text-align:center"># Levels</th>
      <th width="15%">Levels</th>
      <th width="45%">Description</th>
      <th width="5%">Based on</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="center"><strong>P15</strong></td>
      <td><strong>Market</strong></td>
      <td>Number of current and potential consumers of certain services, as well as current and potential providers of these services</td>
      <td align="center">7±2</td>
      <td>-</td>
      <td>The market segmentation can be based on geographic, sociodemographic, psychographic, or behavioral criteria. Market segmentation influences the characteristics and volumes of products at each level.</td>
      <td><a href="#meffert-et-al-2019">Meffert et al. (2019)</a></td>
    </tr>
    <tr>
      <td align="center"><strong>P16</strong></td>
      <td><strong>Distribution channel</strong></td>
      <td>Channel through which the product reaches the end customer</td>
      <td align="center">7±2</td>
      <td>-</td>
      <td>There are two types of sales: direct (without an intermediary) and indirect (with external sales agents). Depending on the application and products being disassembled, corresponding characteristics can be used for grouping. For instance, products sold in retail stores could be categorized as direct sales and grouped into specialty stores, department stores, mail-order companies, and supermarkets.</td>
      <td><a href="#bruhn-2022">Bruhn (2022)</a></td>
    </tr>
    <tr>
      <td align="center"><strong>P17</strong></td>
      <td><strong>Manufacturer</strong></td>
      <td>Manufacturer responsible for manufacturing and supplying the product</td>
      <td align="center">7±2</td>
      <td>-</td>
      <td>Manufacturers can be grouped by their production type (individual/project, small/large series, or mass production) or by their position in the supply chain. Key company figures, such as turnover and number of employees, can also be used.</td>
      <td><a href="#brambring-et-al-2013">Brambring et al. (2013)</a></td>
    </tr>
  </tbody>
</table>

<br>

---

<br>

## 3. System-Related Groups
### 3.1 System Structure and Organization

Table 3.1 presents feature groups addressing the structure and organization of the material flow within disassembly systems. This category focuses on the design and control of material flow paths and the arrangement of materials, machines, and workstations.

**Table 3.1.** System structure and organization feature groups

<table>
  <thead>
    <tr>
      <th width="2%" style="text-align:center">ID</th>
      <th width="8%">Group</th>
      <th width="20%">Definition</th>
      <th width="5%" style="text-align:center"># Levels</th>
      <th width="15%">Levels</th>
      <th width="45%">Description</th>
      <th width="5%">Based on</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="center"><strong>S01</strong></td>
      <td><strong>Division of labor</strong></td>
      <td>Distribution of a specific scope of work among several people or work systems</td>
      <td align="center">3</td>
      <td>• Task division<br>• Quantity division<br>• Mixed form</td>
      <td>The division of labor aims to improve efficiency by specializing the scope of work. In the division by type, several capacity units perform part of the work, whereas in the division by quantity, each capacity unit completes a subset of the work. This decision affects the organization of work and the flow of materials.</td>
      <td><a href="#warnecke-1995">Warnecke (1995)</a></td>
    </tr>
    <tr>
      <td align="center"><strong>S02</strong></td>
      <td><strong>Divisional structure</strong></td>
      <td>Central focus of consideration on which the design of the disassembly system is based</td>
      <td align="center">5</td>
      <td>• Function-oriented<br>• Workflow-oriented<br>• Product-oriented<br>• Resource-oriented<br>• Variant-mix-oriented</td>
      <td>The divisional structure defines the organizational principle of the system and influences its layout and flexibility. In function-oriented systems, resources are grouped by function. Workflow-oriented systems focus on the sequence of work processes and the arrangement of resources. Product-oriented systems align all resources and processes to enable efficient value creation for the product..</td>
      <td><a href="#nyhuis-et-al-2021">Nyhuis et al. (2021)</a></td>
    </tr>
    <tr>
      <td align="center"><strong>S03</strong></td>
      <td><strong>System configuration</strong></td>
      <td>Structural design of a disassembly system in terms of the arrangement, number, type, and interaction of handling devices</td>
      <td align="center">4</td>
      <td>• Single-workstation<br>• Parallel<br>• Line<br>• Hybrid</td>
      <td>Single-workstation systems use a central handling device (typically a robot). <a href="#kahmeyer-1995">Kahmeyer (1995)</a> distinguishes between four system configurations: (1) single-workstation disassembly system with a disassembly workstation and a central handling device (i.e., an industrial robot); (2) parallel disassembly systems with multiple handling devices that perform the same scope of work on different objects; (3) line disassembly systems with multiple handling devices that work on only one object; and (4) hybrid disassembly systems with manual workstations and industrial robots, typically involving a division of labor.</td>
      <td><a href="#kahmeyer-1995">Kahmeyer (1995)</a></td>
    </tr>
    <tr>
      <td align="center"><strong>S04</strong></td>
      <td><strong>Disassembly stages</strong></td>
      <td>Number of sequential disassembly stages representing process segments</td>
      <td align="center">2</td>
      <td>• Staged<br>• Cyclic</td>
      <td>The number of stages in a staged system is determined by the longest path across individual process segments. Cyclic systems return at least one output object as input to the same stage or an upstream one.</td>
      <td><a href="#dyckhoff-spengler-2005">Dyckhoff & Spengler (2005)</a></td>
    </tr>
    <tr>
      <td align="center"><strong>S05</strong></td>
      <td><strong>Decision distribution</strong></td>
      <td>Distribution of decision-making responsibility and authority between humans and systems</td>
      <td align="center">6</td>
      <td>• 0 - Human decides<br>• 1 - Assisted decision-making<br>• 2 - Partial decision-making<br>• 3 - informed decision-making<br>• 4 - Delegated decision-making<br>• 5 - Autonomous decision-making</td>
      <td>The distribution of decision-making ranges from complete human control (level 0), to assisted decision-making (level 1), to system proposals requiring human approval (levels 2-3), to partial system autonomy (level 4), to complete system autonomy (level 5).</td>
      <td><a href="#holtel-et-al-2017">Holtel et al. (2017)</a></td>
    </tr>
    <tr>
      <td align="center"><strong>S06</strong></td>
      <td><strong>Technical changeability</strong></td>
      <td>Ability to adapt entire systems to product and market requirements</td>
      <td align="center">4</td>
      <td>• Rigid multi-machine<br>• Flexible multi-machine<br>• Individual machines<br>• Reconfigurable</td>
      <td>Rigid multi-machine systems offer high productivity but low flexibility. In contrast, flexible multi-machine systems offer moderate productivity and higher flexibility. Single machines have the lowest productivity and variable flexibility, depending on the machine type. Reconfigurable systems achieve high productivity and flexibility, meeting the requirements of increasingly shorter product cycles.</td>
      <td><a href="#westkämper-löffler-2016">Westkämper & Löffler (2016)</a></td>
    </tr>
  </tbody>
</table>

<br>

### 3.2 Workflow Design
Table 3.2 presents feature groups that address the workflow design and the process organization within disassembly systems. This category focuses on the structure and execution of work processes.

**Table 3.2.** Workflow design feature groups

<table>
  <thead>
    <tr>
      <th width="2%" style="text-align:center">ID</th>
      <th width="8%">Group</th>
      <th width="20%">Definition</th>
      <th width="5%" style="text-align:center"># Levels</th>
      <th width="15%">Levels</th>
      <th width="45%">Description</th>
      <th width="5%">Based on</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="center"><strong>S07</strong></td>
      <td><strong>System organization</strong></td>
      <td>Organization of a disassembly system based on the number of different workpieces that can be processed and the annual volume per workpiece</td>
      <td align="center">5</td>
      <td>• Unchained disassembly<br>• Disassembly cell<br>• Flexible disassembly system<br>• Transfer line<br>• Flexible transfer line</td>
      <td>An unchained disassembly system can handle a wide variety of workpieces with low annual volumes. Disassembly cells use individual machines, often operated by robots, to handle higher volumes and greater variety. Flexible disassembly systems integrate machining centers with flexible transport systems for even higher volumes. Transfer lines handle the highest volumes but only a few types of workpieces. Flexible transfer lines increase the flexibility of transfer lines by integrating machining centers and using information technology.</td>
      <td><a href="#dostal-et-al-1982">Dostal et al. (1982)</a></td>
    </tr>
    <tr>
      <td align="center"><strong>S08</strong></td>
      <td><strong>Disassembly type</strong></td>
      <td>Average batch size (lot size) and frequency of repetition of products</td>
      <td align="center">4</td>
      <td>• One-time disassembly<br>• Individual and small series<br>• Series disassembly<br>• Mass disassembly</td>
      <td>The levels are based on the production types described by <a href="#lödding-2016">Lödding (2016)</a> and transferred to the context of disassembly. One-time disassembly has a low production volume and zero repetitions. Individual and small series disassembly systems have low production volumes and few repetitions. Series disassembly is the first to achieve high production volumes and repetition frequencies. Mass disassembly typically organizes disassembly lines according to flow principles for very high volumes.</td>
      <td><a href="#lödding-2016">Lödding (2016)</a></td>
    </tr>
    <tr>
      <td align="center"><strong>S09</strong></td>
      <td><strong>Automation level</strong></td>
      <td>Proportion of autonomous functions in relation to the total functions of a system or technical installation</td>
      <td align="center">3</td>
      <td>• Manual<br>• Semi-automated<br>• Fully automated</td>
      <td>Manual systems consist of one or more workers performing tasks without powered tools. Semi-automated systems perform part of the work cycle using automated programs, while humans are responsible for the rest. Fully automated systems can operate for extended periods without human assistance, eliminating the need for constant operator presence. The degree of automation affects factors such as staffing requirements and investment costs.</td>
      <td><a href="#groover-2016">Groover (2016)</a></td>
    </tr>
    <tr>
      <td align="center"><strong>S10</strong></td>
      <td><strong>Flexibility</strong></td>
      <td>Ability to produce different products and quantity variants despite varying internal and external influences</td>
      <td align="center">3</td>
      <td>• Machine flexibility<br>• Material flexibility<br>• Process flexibility</td>
      <td>The machine flexibility is the ability of a system to perform different workflows based on production control options. Material flexibility stems from the number of material flow paths between disassembly areas and the variety of transportable materials. Process flexibility refers to variability in production processes, enabling efficient production volume control through balanced resource utilization. Together, these types of flexibility determine the system's adaptability to changing requirements.</td>
      <td><a href="#strohhecker-2009">Strohhecker (2009)</a></td>
    </tr>
  </tbody>
</table>

<br>

### 3.3 Material Flow and Logistics
Table 3.3 presents feature groups that address the structuring and control of the material flow and logistics for the movement of components. This category focuses on the spatial organization, transport logistics, and flow coordination.

**Table 3.3.** Material flow and logistics feature groups

<table>
  <thead>
    <tr>
      <th width="2%" style="text-align:center">ID</th>
      <th width="8%">Group</th>
      <th width="20%">Definition</th>
      <th width="5%" style="text-align:center"># Levels</th>
      <th width="15%">Levels</th>
      <th width="45%">Description</th>
      <th width="5%">Based on</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="center"><strong>S11</strong></td>
      <td><strong>Material flow structure</strong></td>
      <td>Distribution of individual capacity units, i.e., disassembly workstations, taking into account spatial and process-specific constraints</td>
      <td align="center">9</td>
      <td>• Single cell<br>• Line<br>• Construction site<br>• Island<br>• Ring<br>• Star<br>• Cross<br>• Network<br>• Grid</td>
      <td>The material flow structure determines how workstations are grouped together. Individual cells handle all steps in one location. Line structures arrange workstations sequentially for standardized processes. Construction site structures are characterized by a stationary product and moving work. Island structures enable parallel processing. Ring structures handle circular processes with return flows. Star, cross, network, and grid structures offer increasing flexibility and complexity in material handling.</td>
      <td><a href="#ciupek-2004">Ciupek (2004)</a></td>
    </tr>
    <tr>
      <td align="center"><strong>S12</strong></td>
      <td><strong>Logistics concept</strong></td>
      <td>Organization of the transport of components to the workstations and the removal of the disassembled components</td>
      <td align="center">3</td>
      <td>• Centralized<br>• Decentralized<br>• Hybrid</td>
      <td>In centralized logistics, all workstations are supplied from one location, which simplifies coordination but can create bottlenecks. Decentralized logistics uses multiple warehouse locations to supply workstations, which increases flexibility but complicates control. Hybrid concepts combine centralized storage for frequently used materials with decentralized storage for specialized or location-specific components.</td>
      <td><a href="#ciupek-2004">Ciupek (2004)</a>, <a href="#alicke-2005">Alicke (2005)</a></td>
    </tr>
    <tr>
      <td align="center"><strong>S13</strong></td>
      <td><strong>Material flow complexity</strong></td>
      <td>Effort required to control and coordinate material movement depending on the number of preceding and subsequent workstations and the frequency and number of material returns in the disassembly system</td>
      <td align="center">3</td>
      <td>• Linear material flow<br>• Complex without backflow<br>• Complex with backflow</td>
      <td>In linear material flows, each workstation has at most one predecessor and one successor, with no return flows. Complex material flows without return flows can have several predecessor and successor workstations but still maintain unidirectional flow. Complex material flows with return flows are characterized by multiple workstation connections, as well as circular material returns. <a href="#dyckhoff-spengler-2005">Dyckhoff & Spengler (2005)</a> describe another possibility that can be used for grouping according to the material flow complexity. They distinguish between continuous, converging, diverging, and regrouping material flows.</td>
      <td><a href="#lödding-2016">Lödding (2016)</a>, <a href="#dyckhoff-spengler-2005">Dyckhoff & Spengler (2005)</a></td>
    </tr>
    <tr>
      <td align="center"><strong>S14</strong></td>
      <td><strong>Transport intensity</strong></td>
      <td>Transport quantity between two operating resources over a period of time</td>
      <td align="center">7±2</td>
      <td>-</td>
      <td>The transport intensity quantifies the movement of materials between two pieces of equipment. It can be measured by the number of trips, the weight of the materials transported, how often they are transported, or the cost of covering the distance.</td>
      <td><a href="#vdi-3595">VDI 3595</a></td>
    </tr>
    <tr>
      <td align="center"><strong>S15</strong></td>
      <td><strong>Parts flow</strong></td>
      <td>Movement of workpieces or assemblies between workstations within a disassembly system</td>
      <td align="center">4</td>
      <td>• Batch transport<br>• One-piece-flow<br>• Overlapping<br>• Batch production</td>
      <td>In batch processing, an entire batch is processed at one workstation before any component is passed on. In one-piece flow, each component moves to the next workstation immediately after being processed. In overlapping production, some of a batch is passed on early while the rest continues to be processed. Batch production involves processing several batches of the same type together. The organization of the flow of components affects the efficiency and the flexibility of the process, and the control effort.</td>
      <td><a href="#lödding-2016">Lödding (2016)</a></td>
    </tr>
  </tbody>
</table>

<br>

### 3.4 Strategy
Table 3.4 presents feature groups that address the decisions regarding the long-term orientation and structure of a disassembly system.

**Table 3.4.** Strategy feature groups

<table>
  <thead>
    <tr>
      <th width="2%" style="text-align:center">ID</th>
      <th width="8%">Group</th>
      <th width="20%">Definition</th>
      <th width="5%" style="text-align:center"># Levels</th>
      <th width="15%">Levels</th>
      <th width="45%">Description</th>
      <th width="5%">Based on</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="center"><strong>S16</strong></td>
      <td><strong>Resource strategy</strong></td>
      <td>Alignment of a disassembly system with regard to the organization and control of material supply</td>
      <td align="center">4</td>
      <td>• Warehousing<br>• Logistics centers<br>• Just-in-Time (JIT)<br>• Just-in-Sequence (JIS)</td>
      <td>In warehousing, components are kept in stock to ensure security of supply. Logistics centers consolidate components from different suppliers centrally and distribute them further. With JIT, components are delivered on demand and on time. JIS extends JIT to include sequential delivery in the order of disassembly.</td>
      <td><a href="#hummel-2019">Hummel (2019)</a></td>
    </tr>
    <tr>
      <td align="center"><strong>S17</strong></td>
      <td><strong>Disassembly strategy</strong></td>
      <td>Alignment of a company with regard to the scheduling and quantity planning of disassembly processes</td>
      <td align="center">2</td>
      <td>• Disassemble-to-Order (DTO)<br>• Disassemble-to-Stock (DTS)</td>
      <td>The definitions of <a href="#syska-2006">Syska (2006)</a> are applied to the disassembly context. With DTO, disassembly occurs when there is a specific need or customer order. With DTS, however, returned products are disassembled regardless of specific orders to make components available in the warehouse.</td>
      <td><a href="#syska-2006">Syska (2006)</a></td>
    </tr>
  </tbody>
</table>

<br>

---

<br>

## References

#### Alicke 2005
Alicke, K., 2005. Planung und Betrieb von Logistiknetzwerken: Unternehmensübergreifendes Supply Chain Management. 2., neu bearb. und erw. aufl. ed., Springer, Berlin and Heidelberg.

#### Bayerisches Landesamt für Umwelt 2022
Bayerisches Landesamt für Umwelt, 2022. Einfach effizient! Maßnahmen zur Steigerung der Ressourceneffizienz.

#### Brambring et al. 2013
Brambring, F., Hauptvogel, A., Hempel, T., Hering, N., Luckert, M., Maasem, C., Meißner, J., Reschke, J., Schnittler, V., 2013. Produktion am Standort Deutschland: Ergebnisse der Untersuchung 2013.

#### Bruhn 2022
Bruhn, M., 2022. Marketing: Grundlagen für Studium und Praxis. moremedia. 15., überarbeitete und erweiterte auflage ed., Springer Fachmedien Wiesbaden, Wiesbaden. https://doi.org/10.1007/978-3-658-36298-0.

#### Callister & Rethwisch 2018
Callister, W.D., Rethwisch, D.G., 2018. Materials science and engineering: An introduction. 10th edition ed., Wiley, Hoboken NJ.

#### Ciupek 2004
Ciupek, M., 2004. Beitrag zur simulationsgestützten Planung von Demontagefabriken für Elektro- und Elektronikaltgeräte. Dissertation.

#### Dostal et al. 1982
Dostal, W., Kamp, A.W., Lahner, M., Seessle, W.P., 1982. Flexible Fertigungssysteme und Arbeitsplatzstrukturen. Mitteilungen aus der Arbeitsmarkt- und Berufsforschung 15.

#### Dyckhoff & Spengler 2005
Dyckhoff, H., Spengler, T.S., 2005. Produktionswirtschaft: Eine Einführung für Wirtschaftsingenieure. Springer-Lehrbuch, Springer, Berlin and Heidelberg.

#### Fritz et al. 2023
Fritz, D., Heinfellner, H., Lambert, S., 2023. Rohstoffe der Elektromobilität: Kurzstudie zur Analyse derzeitiger und möglicher künftiger Rohstoffabhängigkeiten von Elektrofahrzeugen. volume REP-0850 of Perspektiven für Umwelt & Gesellschaft. Umweltbundesamt GmbH, Wien. URL: https://www.umweltbundesamt.at/fileadmin/site/publikationen/rep0850.pdf.

#### Giudice 2010
Giudice, F., 2010. Disassembly depth distribution for ease of service: a rule-based approach. Journal of Engineering Design 21, 375–411. https://doi.org/10.1080/09544820802282504.

#### Göpfert 1998
Göpfert, J., 1998. Modulare Produktentwicklung: Zur gemeinsamen Gestaltung von Technik und Organisation: Zugl.: München, Univ., Diss., 1998. Gabler-Edition Wissenschaft Markt- und Unternehmensentwicklung, Dt. Univ.-Verl. and Gabler, Wiesbaden. https://doi.org/10.1007/978-3-663-08152-4.

#### Greitmann 1998
Greitmann, G., 1998. Micromechanical Tactile Gripper System for MicroAssembly. Dissertation. Friedrich-Alexander-Universität Erlangen-Nürnberg. Nürnberg.

#### Groover 2016
Groover, M.P., 2016. Automation, production systems, and computer-integrated manufacturing. Fourth edition, global edition ed., Pearson, Boston and Columbus and Indianapolis.

#### Holtel et al. 2017
Holtel, S., Hufenstuhl, A., Klug, A., 2017. Künstliche Intelligenz verstehen als Automation des Entscheidens: Leitfaden.

#### Huber 2001
Huber, A., 2001. Demontageplanung und -steuerung: Planung und Steuerung industrieller Demontageprozesse mit PPS-Systemen: Zugl.: Magdeburg, Univ., Diss., 2001 u.d.T.: Huber, Alexander: Planung und Steuerung industrieller Demontageprozesse mit PPS-Systemen. Magdeburger Schriften zur Wirtschaftsinformatik, Shaker, Aachen.

#### Hummel 2019
Hummel, T., 2019. Praxishandbuch JIT/JIS mit SAP®: Die Just-in-Time und Just-in-Sequence Abwicklung mit SAP®. Springer Vieweg, Berlin. https://doi.org/10.1007/978-3-662-58512-2.

#### Jordan et al. 2024
Jordan, P., Kroeger, S., Streibel, L., Vernim, S., Zaeh, M.F., 2024. Concept for a data-based approach to support decision-making in tactical tasks for planning disassembly systems. Procedia CIRP 122, 288–293. https://doi.org/10.1016/j.procir.2024.01.042.

#### Jordan et al. 2025
Jordan, P., Streibel, L., Haider, C., Schneider, D., Zaeh, M.F., 2025. Subsystems and influencing factors enabling simulation for planning disassembly systems, in: Drossel, W.G., Ihlenfeldt, S., Dix, M. (Eds.), Production at the Leading Edge of Technology. Springer Nature Switzerland, Cham. Lecture Notes in Production Engineering, pp. 568–578. https://doi.org/10.1007/978-3-031-86893-1_62.

#### Kahmeyer 1995
Kahmeyer, M., 1995. Flexible Demontage mit dem Industrieroboter am Beispiel von Fernsprech-Endgeräten: Zugl.: Stuttgart, Univ., Diss., 1995. volume 215 of IPA-IAO-Forschung und Praxis. Springer, Berlin and Heidelberg.

#### Kalaycilar et al. 2024
Kalaycilar, E.G., Azizoğlu, M., Batun, S., 2024. Disassembly line balancing with hazardous task failures – Model based solution approaches. Computers & Industrial Engineering 190, 110089. https://doi.org/10.1016/j.cie.2024.110089.

#### Kim & Ki Moon 2017
Kim, S., Ki Moon, S., 2017. Disassembly Complexity-Driven Module Identification for Additive Manufacturing. Ph.D. thesis. https://doi.org/10.3233/978-1-61499-779-5-782.

#### Lespant 2021
Lespant, G., . Die Rolle der kritischen Metalle bei der Energiewende: Herausforderungen und Strategien. URL: https://shs.hal.science/halshs-03364930v1.

#### Lödding 2016

Lödding, H., 2016. Verfahren der Fertigungssteuerung: Grundlagen, Beschreibung, Konfiguration. VDI-Buch. 3. Auflage ed., Springer Vieweg, Berlin and Heidelberg. https://doi.org/10.1007/978-3-662-48459-3.

#### Meffert et al. 2019
Meffert, H., Burmann, C., Kirchgeorg, M., Eisenbeiß, M., 2019. Marketing: Grundlagen marktorientierter Unternehmensführung Konzepte - Instrumente - Praxisbeispiele. Springer eBook Collection. 13., überarbeitete und erweiterte auflage ed., Springer Gabler, Wiesbaden. https://doi.org/10.1007/978-3-658-21196-7.

#### Miller 1995
Miller, G., 1995. The magical number seven, plus or minus two some limits on our capacity for processing information. Psychological Review 101, 343–352.


#### Nyhuis et al. 2021
Nyhuis, P., Rochow, N.E., Krause, M., Pischke, D., Seitz, M., Kuprat, V.K., 2021. Organisationsformen der Produktion https://doi.org/10.15488/11332.

#### Ohlendorf 2006
Ohlendorf, M., 2006. Simulationsgestützte Planung und Bewertung von Demontagesystemen. Dissertation. Essen.

#### Plötner 2017
Plötner, M., 2017. Integriertes Vorgehen zur selbstindividualisierungsgerechten Produktstrukturplanung. Dissertation. Technischen Universität München. München.

#### Porter 1998
Porter, M.E., 1998. Competitive strategy: Techniques for analyzing industries and competitors ; with a new introduction. Free Press, New York, NY.

#### Poschmann et al. 2020
Poschmann, H., Brüggemann, H., Goldmann, D., 2020. Robotized Disassembly as an Essential Driver for Digitalization in Future Recycling Processes, in: Holm, O., Thomé-Kozmiensky, E., Goldmann, D., Friedrich, B. (Eds.), Recycling und Rohstoffe. Thomé-Kozmiensky Verlag GmbH, Neuruppin, pp. 570–584.

#### Rieker 2018
Rieker, T., 2018. Modellierung der Zuverlässigkeit technischer Systeme mit stochastischen Netzverfahren. Dissertation. Uni Stuttgart. Stuttgaert.

#### Scheller 1998
Scheller, H. (Ed.), 1998. Automatisierte Demontagesysteme und recyclinggerechte Produktgestaltung elektronischer Baugruppen: Zugl.: Erlangen, Nürnberg, Univ., Diss., 1997. volume 74 of Fertigungstechnik - Erlangen. Meisenbach, Bamberg.

#### Stammen-Hegener 2002
Stammen-Hegener, C., 2002. Simultane Losgrößen- und Reihenfolgeplanung bei ein- und mehrstufiger Fertigung. Gabler Edition Wissenschaft, Deutscher Universitätsverlag, Wiesbaden and s.l. https://doi.org/10.1007/978-3-663-11367-6.

#### Strohhecker 2009
Strohhecker, J., Größler, A. (Eds.), 2009. Strategisches und operatives Produktionsmanagement: Empirie und Simulation. Gabler Research. 1. Aufl. ed., Gabler, Wiesbaden.

#### Syska 2006
Syska, A., 2006. Produktionsmanagement: Das A - Z wichtiger Methoden und Konzepte für die Produktion von heute. 1. Aufl. ed., Gabler Verlag, s.l.

#### Ullerich & Buscher 2013
Ullerich, C., Buscher, U., 2013. Flexible disassembly planning considering product conditions. International Journal of Production Research 51, 6209–6228. https://doi.org/10.1080/00207543.2013.825406.

#### VDI 3595
VDI Verein Deutscher Ingenieure e.V., 1999. Methoden zur materialflußgerechten Zuordnung von Betriebsbereichen und -mitteln.

#### Warnecke 1995
Warnecke, H.J., 1995. Der Produktionsbetrieb 2: Produktion, Produktionssicherung. volume 2 of Springer-Lehrbuch. 3., unveränderte Aufl. ed., Springer Berlin Heidelberg, Berlin, Heidelberg. https://doi.org/10.1007/978-3-642-79241-0.

#### Westkämper & Löffler 2016
Westkämper, E., Löffler, C., 2016. Strategien der Produktion. Springer Berlin Heidelberg, Berlin, Heidelberg. https://doi.org/10.1007/978-3-662-48914-7.
