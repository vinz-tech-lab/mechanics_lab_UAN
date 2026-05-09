import streamlit as st
import streamlit.components.v1 as components
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from matplotlib.lines import Line2D

# --- Page Configuration ---
st.set_page_config(page_title="Mechanical properties Number UAN", layout="wide")
st.title("🔬 Mechanical properties Number UAN")

# --- Matplotlib dark style to match the Streamlit theme ---
plt.rcParams.update({
    "figure.facecolor":  "#0e1117",
    "axes.facecolor":    "#1e1e1e",
    "axes.edgecolor":    "#888888",
    "axes.labelcolor":   "#dddddd",
    "axes.titlecolor":   "#ffffff",
    "xtick.color":       "#bbbbbb",
    "ytick.color":       "#bbbbbb",
    "grid.color":        "#333333",
    "text.color":        "#dddddd",
    "savefig.facecolor": "#0e1117",
    "font.size":         11,
    "axes.titlesize":    13,
    "axes.labelsize":    12,
    "legend.facecolor":  "#262730",
    "legend.edgecolor":  "#444444",
    "legend.labelcolor": "#dddddd",
})

# --- Helper: gated "hidden" exercise ---
def hidden_exercise(key_prefix, gate_question, exercise_md, hint=None,
                    accepted_answers=None, numeric_target=None, numeric_tolerance=None,
                    title="🔒 Hidden bonus exercise — answer the gate question to unlock"):
    """
    Renders a *collapsed* expander whose label only hints that an exercise exists.
    When the student opens it, a gate question is shown. They must type the correct
    answer (string match against `accepted_answers`, OR numeric within
    `numeric_tolerance` of `numeric_target`) to reveal the bonus exercise.

    Once unlocked in a session, it stays unlocked across reruns.
    """
    unlocked_key = f"{key_prefix}_unlocked"
    if unlocked_key not in st.session_state:
        st.session_state[unlocked_key] = False

    def _normalize(s):
        return (s or "").strip().lower().replace("%", "").replace(" ", "").replace(",", ".")

    def _is_correct(ans):
        norm = _normalize(ans)
        if accepted_answers:
            if norm in [_normalize(a) for a in accepted_answers]:
                return True
        if numeric_target is not None and numeric_tolerance is not None:
            try:
                v = float(norm)
                if abs(v - numeric_target) <= numeric_tolerance:
                    return True
            except ValueError:
                pass
        return False

    with st.expander(title):
        if st.session_state[unlocked_key]:
            st.success("🔓 **UNLOCKED** — bonus exercise below.")
            st.markdown(exercise_md)
            return

        st.markdown(f"**🔑 Gate question:** {gate_question}")
        if hint:
            st.caption(f"💡 *Hint:* {hint}")
        ans = st.text_input(
            "Type your answer to unlock the bonus exercise:",
            key=f"{key_prefix}_input",
            placeholder="Your answer here…",
        )
        if ans:
            if _is_correct(ans):
                st.session_state[unlocked_key] = True
                st.success("🔓 **UNLOCKED** — bonus exercise below.")
                st.markdown(exercise_md)
            else:
                st.warning("Not quite — re-read the theory deep-dive in this tab and try again. The answer is hidden somewhere in the formulas above.")


# --- UI Setup ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "👋 Welcome & Registration", 
    "📈 Stress-Strain Curve", 
    "⚛️ Dislocations & Defects", 
    "📏 Hall-Petch Theory", 
    "⚡ Atomic Origin of Modulus", 
    "📝 Assessment"
])

# ==========================================
# TAB 1: WELCOME & REGISTRATION
# ==========================================
with tab1:
    st.header("Welcome to the Materials Engineering Laboratory")

    st.markdown("""
    In this interactive virtual laboratory you will explore the fundamental mechanical
    properties of materials, **bridging the gap between macroscopic engineering behaviour
    and atomic-scale physics**.  Each tab is a self-contained micro-experiment with
    its own simulator, theory, and "how to play" guide.
    """)

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("📚 Module roadmap")
        st.markdown("""
| Tab | Focus | Tool you will use |
|---|---|---|
| 📈 **Stress–Strain** | Tensile test of 12 materials | Live virtual UTM |
| ⚛️ **Defects** | Why metals deform (dislocations) | Animated lattice |
| 📏 **Hall–Petch** | Grain-size strengthening | Comparative tensile rig |
| ⚡ **Atomic Origin** | Where stiffness comes from | LJ vs Morse explorer |
| 📝 **Assessment** | 10-question evaluation | Curve-reading + theory |
""")

    with col_b:
        st.subheader("🎯 Learning objectives")
        st.markdown("""
By the end of the lab you should be able to:
1. **Read** a stress–strain curve and extract $E$, $\\sigma_y$, $\\sigma_{UTS}$ and $\\varepsilon_f$.
2. **Apply** the 0.2 % offset method to ductile metals.
3. **Explain** plasticity in terms of dislocation glide and pile-up at grain boundaries.
4. **Predict** the effect of grain refinement using $\\sigma_y = \\sigma_0 + k/\\sqrt{d}$.
5. **Connect** Young's modulus to the curvature of the interatomic potential
   $E \\approx (1/r_0)\\,\\partial^2 U/\\partial r^2|_{r_0}$.
""")

    st.divider()

    st.subheader("🕹️ How to drive the simulator (general rules)")
    st.markdown("""
- Each interactive tab has a **left control panel** (material selector, sliders, toggles)
  and a **right simulation panel** with three live canvases:
  *Macro specimen* (the dog-bone you stretch), *Micro physics*
  (what happens inside the material), and the *Stress–strain plot* drawn in real time.
- Press the big red **🚀 Start Tensile Test** (or **▶ Animate Bond Stretch**) button
  at the top of the simulator. The button turns into **RESET** when the run finishes.
- Change the material/grain/potential **before** pressing Start. The simulator rebuilds
  itself when a control changes.
- Use the **Testing Speed** slider to slow runs down: 0.5 × is good for capturing
  the elastic→plastic transition by eye; 3 × is good for quickly comparing many materials.
""")

    st.divider()

    # Registration logic
    student_name = st.text_input("📝 Please register your name to begin the session:")
    if student_name:
        st.success(f"Welcome, {student_name}! You may now proceed through the tabs to begin the laboratory.")

# ==========================================
# TAB 2: STRESS-STRAIN CURVE
# ==========================================
with tab2:
    st.header("The Stress-Strain Curve")
    st.markdown(r"""
    The stress–strain curve is the foundational roadmap of a material's mechanical behaviour.
    It is generated by applying a gradual tensile load to a specimen and plotting the
    **Engineering Stress** $\sigma = F/A_0$ against the **Engineering Strain**
    $\varepsilon = \Delta L / L_0$, where $A_0$ and $L_0$ are the *original* (undeformed)
    cross-section and gauge length.

    ### Key regions and points
    * **Elastic region.** Initial linear portion. Deformation is reversible (Hooke's law,
      $\sigma = E\varepsilon$). The slope is **Young's modulus $E$**.
    * **Yield strength (YS or $\sigma_y$).** The stress at which permanent (plastic)
      deformation begins. For materials without a sharp yield point, the
      **0.2 % offset method** is used (see toggle on the right).
    * **Strain hardening.** As the metal deforms plastically, dislocations multiply and
      tangle, forcing the flow stress to rise. The Hollomon equation
      $\sigma = K\varepsilon^n$ captures this in many metals.
    * **Ultimate tensile strength (UTS, $\sigma_u$).** Maximum engineering stress. After
      this point the cross-section narrows locally — *necking* — and the load drops.
    * **Fracture point.** Final separation, at engineering strain $\varepsilon_f$.
    """)

    with st.expander("📚 Theory deep-dive: engineering vs true stress, work of fracture, ductile vs brittle"):
        st.markdown(r"""
**Engineering vs true stress.** Engineering stress uses the original area $A_0$, so the
curve drops after necking. True stress $\sigma_T = F/A_i$ uses the *instantaneous* area and
keeps rising until fracture. They are related by
$\sigma_T = \sigma(1+\varepsilon)$ and $\varepsilon_T = \ln(1+\varepsilon)$,
valid up to the onset of necking.

**Resilience and toughness.** The area under the elastic part of the curve is the
**modulus of resilience** $U_r = \sigma_y^2/(2E)$ — the elastic energy a unit volume
can absorb without permanent damage. The total area under the curve up to fracture is the
**modulus of toughness** $U_T \approx \int_0^{\varepsilon_f} \sigma\, d\varepsilon$ —
the total energy absorbed.

**Necking criterion (Considère).** Necking begins when geometric softening
($dA/A = -d\varepsilon$) overtakes work hardening ($d\sigma/\sigma$). For a Hollomon
material $\sigma=K\varepsilon^n$, this gives a true strain at necking
$\varepsilon_T^{neck}=n$ — exactly the strain-hardening exponent.

**Why the curves look so different across material classes**
* **Ductile metals** (steel, Cu, Al) — long plastic plateau, work hardening, necking;
  fracture at 10–60 % strain.
* **High-strength metals** (Ti-6Al-4V, hard steels) — short plateau, high $\sigma_y$.
* **Ceramics** (Al₂O₃, ZrO₂) — perfectly linear up to brittle fracture at < 0.5 % strain.
  No yield, $E$ is huge, but the **Weibull-distributed flaws** make strength size-dependent.
* **Polymers** (PEEK) — yield drop, cold drawing (chains align), then re-strengthening.
* **Elastomers** (rubber) — non-linear from $\varepsilon=0$, S-shaped, follow rubber
  elasticity $\sigma \approx (E/3)(\lambda - 1/\lambda^2)$.
* **CNTs** — linear-elastic right up to brittle break at $E\approx 1$ TPa.
* **Biopolymers** (spider silk) — characteristic *J-curve*: soft amorphous matrix yields,
  then $\beta$-sheet crystals lock in and stiffen the response.
* **Superelastic alloys** (Nitinol) — stress-induced austenite → martensite transformation
  produces a flat plateau on loading and a *hysteresis loop* on unloading.

**Standards.** Tensile testing follows **ASTM E8/E8M** (metals) and **ISO 6892-1**
(metals, room temperature). Both define the dog-bone geometry, the strain rate
($\sim 10^{-3}\,\text{s}^{-1}$), and the 0.2 % offset construction used here.
""")

    with st.expander("🕹️ How to play with this simulator — guided exercises"):
        st.markdown("""
**The dashboard up top** reports six live numbers as the test runs:

| Read-out | Meaning |
|---|---|
| **Strain $\\varepsilon$** | Current engineering strain $\\Delta L/L_0$ |
| **Stress $\\sigma$** | Current engineering stress $F/A_0$ in MPa |
| **Tangent $E$ (init)** | Constant — the slope $d\\sigma/d\\varepsilon$ at $\\varepsilon=0$ |
| **Secant $E$ (live)** | Live $\\sigma/\\varepsilon$ — equals tangent in elastic regime, drops once plasticity begins |
| **Min Area** | Cross-section at the narrowest neck (mm²). Watch it collapse during necking |
| **0.2 % Offset YS** | Only visible if you toggle the offset construction on |

**Exercise 1 — measure $E$ yourself.** Pick *Structural Steel*, set Speed = 0.5×, press Start.
Read the dashboard at $\\varepsilon = 0.001$. Compute $E_{est} = \\sigma/\\varepsilon$.
Compare with the catalog value 200 GPa.

**Exercise 2 — find the yield point.** Watch the *Secant E (live)* number while running.
The exact instant it starts to drop below the *Tangent E (init)* value is yielding.
Note the strain — it should match $\\varepsilon_y = \\sigma_y/E \\approx 250/200000 = 0.00125$.

**Exercise 3 — see the 0.2 % offset construction in action.** Toggle on
*Show 0.2 % Offset Yield Construction*. Re-run with Aluminium 7075-T6. Observe the
yellow elastic line, the orange offset-line at $\\varepsilon = 0.002$, and the cyan dot
where they hit the curve — that is **Rp0.2**.

**Exercise 4 — compare brittle vs ductile.** Run *Alumina (Al₂O₃)* — fracture at
0.07 %! Now run *Natural Rubber* — strain to 600 %. Same physics, vastly different
material classes. Note that ceramics show **no necking** because they have no plastic
regime to neck into.

**Exercise 5 — necking.** Run Steel A36 with Speed = 0.5×. Watch the Min Area read-out
*and* the dog-bone. Past $\\varepsilon \\approx 0.12$ the centre narrows visibly while
the engineering stress drops. This is the Considère criterion in action.

**Exercise 6 — superelasticity.** Run *Nitinol*. The test loads to peak strain *then
unloads* — drawing the full hysteresis loop. The shaded micro panel toggles between
"Austenite → Martensite" (loading) and "Martensite → Austenite" (unloading).

**Exercise 7 — bio-mechanics.** Run *Spider Silk (Dragline)*. Notice the J-shape — soft
start, then dramatic stiffening near $\\varepsilon \\approx 0.3$. This is why a spider's
web absorbs the kinetic energy of a hitting insect without snapping.
""")

    with st.expander("📐 Worked exercises with formulas — solve these by hand"):
        st.markdown(r"""
Each problem gives you raw data and a formula to apply. Work through them with a calculator
**before** running the simulator — the simulator then becomes a check on your arithmetic and
intuition, not the source of the answer.

---

### Exercise 1 — Engineering stress and strain from raw test data
A round-bar tensile specimen has initial diameter $d_0 = 12.5$ mm and gauge length $L_0 = 50.0$ mm.
At an applied load of $F = 49\,050$ N the gauge reads 50.10 mm.

**Formulas.** $A_0 = \pi d_0^2/4$ &nbsp;&nbsp; $\sigma = F/A_0$ &nbsp;&nbsp; $\varepsilon = \Delta L/L_0$

**Solution.**
- $A_0 = \pi(12.5)^2/4 = 122.7\;\text{mm}^2$
- $\sigma = 49050/122.7 = \mathbf{399.8\;\text{MPa}}$
- $\varepsilon = 0.10/50.0 = \mathbf{0.0020}\;(0.20\,\%)$

---

### Exercise 2 — Convert engineering → true stress and strain
Same specimen, but pulled until $\varepsilon = 0.20$ at $\sigma = 500$ MPa.
Assume incompressible plastic flow.

**Formulas.** $\sigma_t = \sigma(1+\varepsilon)$ &nbsp;&nbsp; $\varepsilon_t = \ln(1+\varepsilon)$

**Solution.**
- $\sigma_t = 500 \times 1.20 = \mathbf{600\;\text{MPa}}$ (engineering under-reports true stress by 20 %!)
- $\varepsilon_t = \ln(1.20) = \mathbf{0.182}$ (true strain under-reports engineering by 9 %)

> **Take-away.** At small strain ($\varepsilon < 0.01$) the two coincide. Past necking the gap explodes —
> always plot true stress vs true strain when computing flow curves.

---

### Exercise 3 — Modulus of resilience (elastic energy stored at yield)
A36 steel: $\sigma_y = 250$ MPa, $E = 200$ GPa.

**Formula.** $U_r = \dfrac{\sigma_y^{\,2}}{2E}$

**Solution.** $U_r = (250\times 10^6)^2 / (2\times 200\times 10^9) = \mathbf{156.3\;\text{kJ/m}^3}$

This is the maximum elastic energy per unit volume the material can absorb without permanent deformation —
recovered as the load is removed. Springs are designed to maximize $U_r$ (high $\sigma_y$, moderate $E$).

---

### Exercise 4 — Hollomon's law: extract $n$ and $K$ from two flow-curve points
On the plastic regime: at $\varepsilon_p = 0.05$, $\sigma_t = 480$ MPa; at $\varepsilon_p = 0.15$, $\sigma_t = 600$ MPa.

**Formula.** $\sigma_t = K\,\varepsilon_p^{\,n}\;\Rightarrow\; \ln(\sigma_2/\sigma_1) = n\ln(\varepsilon_2/\varepsilon_1)$

**Solution.**
- $n = \ln(600/480)/\ln(0.15/0.05) = \ln(1.25)/\ln(3) = 0.223/1.099 = \mathbf{0.203}$
- $K = 600/(0.15)^{0.203} = 600/0.682 = \mathbf{880\;\text{MPa}}$

---

### Exercise 5 — Considère criterion: predict the necking strain
For a Hollomon material, the onset of diffuse necking obeys $d\sigma_t/d\varepsilon_t = \sigma_t$,
which simplifies to $\varepsilon_t^{\,*} = n$.

**Solution.** With $n = 0.203$ from Ex 4, $\varepsilon_{\text{uniform}} \approx \mathbf{0.20}$.
Past this point deformation localizes into a neck; the engineering stress drops while true stress keeps rising.

---

### Exercise 6 — Modulus of toughness (area under $\sigma$–$\varepsilon$)
Trapezoidal approximation for a ductile metal: $U_T \approx \tfrac{1}{2}(\sigma_y + \sigma_{UTS})\,\varepsilon_f$.

**Solution for ductile A36** ($\sigma_y=250$, $\sigma_{UTS}=400$ MPa, $\varepsilon_f=0.25$):
$$U_T = \tfrac{1}{2}(250+400)(0.25) = \mathbf{81.3\;\text{MJ/m}^3}$$

**Brittle alumina** ($\sigma_f=260$ MPa, $\varepsilon_f=7\times 10^{-4}$):
$$U_T \approx \tfrac{1}{2}(260)(7\times 10^{-4}) = \mathbf{0.091\;\text{MJ/m}^3}$$

> **The steel absorbs ~900× more energy before fracture.** This is why ductile metals make better
> structural materials than ceramics — they tolerate overload by deforming plastically.

---

### Exercise 7 — Shear modulus from $E$ and $\nu$ (isotropic)
For copper, $E = 130$ GPa, $\nu = 0.34$.

**Formula.** $G = \dfrac{E}{2(1+\nu)}$

**Solution.** $G = 130/(2\times 1.34) = \mathbf{48.5\;\text{GPa}}$
(Tabulated value for Cu: 48 GPa — agreement to within 1 %.)

---

### Exercise 8 — Measure Poisson's ratio from a tensile test
Initial diameter 10.000 mm. At axial strain $\varepsilon_{\text{axial}} = 0.0030$ the diameter
measures 9.991 mm.

**Formula.** $\nu = -\dfrac{\varepsilon_{\text{transverse}}}{\varepsilon_{\text{axial}}}$

**Solution.**
- $\varepsilon_{\text{trans}} = (9.991-10.000)/10.000 = -9.0\times 10^{-4}$
- $\nu = -(-9.0\times 10^{-4})/(3.0\times 10^{-3}) = \mathbf{0.30}$ (typical metal)

---

### Exercise 9 — Anelastic strain at failure (steel rebar)
A 16 mm rebar, $L_0 = 200$ mm, is loaded to fracture at $\sigma_f = 550$ MPa, $\varepsilon_f = 0.18$.
Compute the **plastic** elongation that remains after the bar fractures and the elastic part snaps back.

**Formulas.** $\varepsilon_{\text{elastic}} = \sigma_f/E$ &nbsp;&nbsp; $\varepsilon_{\text{plastic}} = \varepsilon_f - \varepsilon_{\text{elastic}}$

**Solution** ($E = 200$ GPa):
- $\varepsilon_{\text{elastic}} = 550/200000 = 0.00275$
- $\varepsilon_{\text{plastic}} = 0.18 - 0.003 = \mathbf{0.177}$
- Permanent gauge elongation $= 0.177 \times 200\;\text{mm} = \mathbf{35.4\;\text{mm}}$
""")

    # ---- Hidden bonus exercise (gated) ----
    hidden_exercise(
        key_prefix="t2_bonus",
        title="🔒 Hidden bonus exercise — explore the worked exercises above to unlock",
        gate_question=(
            "In *Worked Exercise 6* above we computed the modulus of toughness of A36 steel. "
            "What value (in **MJ/m³**, integer) was obtained?"
        ),
        hint="Look at the bold number in the steel calculation — round to the nearest integer.",
        accepted_answers=["81", "80", "82", "79", "83", "81.3"],
        numeric_target=81,
        numeric_tolerance=2.5,
        exercise_md=r"""
### 🏆 Bonus — When 'engineering' becomes wildly misleading: rubber at 400 % strain

A natural-rubber band is stretched until $\varepsilon_{\text{eng}} = 4.00$ (i.e. 400 %).
The engineering stress at that point is measured as $\sigma_{\text{eng}} = 8$ MPa.

**Compute three quantities and reflect on the result:**

(i) The **true strain** $\varepsilon_t = \ln(1 + \varepsilon_{\text{eng}})$.

(ii) The **true stress** $\sigma_t = \sigma_{\text{eng}}(1 + \varepsilon_{\text{eng}})$.

(iii) The **ratio** $\sigma_t/\sigma_{\text{eng}}$.

---

**Solution.**
- (i) $\varepsilon_t = \ln(5.00) = \mathbf{1.609}$
- (ii) $\sigma_t = 8 \times 5.00 = \mathbf{40\;\text{MPa}}$
- (iii) $\sigma_t/\sigma_{\text{eng}} = \mathbf{5.00}$

> **Reflection.** At small strain the two definitions coincide (Ex 1 vs Ex 2 in the worked
> set differed by < 1 % at $\varepsilon=0.002$). At rubber-band strains, *engineering stress
> under-reports the true load by a factor of five*. This is why elastomer test reports must
> always state the strain measure used, and why finite-element codes for rubber switch to
> hyperelastic strain-energy models (Mooney-Rivlin, Ogden) instead of Hookean stress-strain.
""",
    )

    st.divider()

    materials = {
        "Structural Steel (A36)": {"name": "Steel A36", "E": 200000, "YS": 250, "UTS": 400, "max_strain": 0.20, "color": "#708090", "type": "metal", "grain_size": "medium", "poisson": 0.30, "n": 0.25, "has_plateau": True,  "soft": 0.30},
        "Aluminum (7075-T6)":     {"name": "Aluminum",  "E": 71700,  "YS": 503, "UTS": 572, "max_strain": 0.11, "color": "#C0C0C0", "type": "metal", "grain_size": "medium", "poisson": 0.33, "n": 0.10, "has_plateau": False, "soft": 0.20},
        "Titanium (Ti-6Al-4V)":   {"name": "Titanium",  "E": 114000, "YS": 880, "UTS": 950, "max_strain": 0.14, "color": "#A9A9A9", "type": "metal", "grain_size": "small",  "poisson": 0.34, "n": 0.10, "has_plateau": False, "soft": 0.20},
        "CoCrMo Alloy":           {"name": "CoCrMo",    "E": 210000, "YS": 500, "UTS": 700, "max_strain": 0.08, "color": "#B0C4DE", "type": "metal", "grain_size": "medium", "poisson": 0.30, "n": 0.15, "has_plateau": False, "soft": 0.18},
        "nc-Copper (~30nm)":      {"name": "nc-Copper", "E": 110000, "YS": 750, "UTS": 800, "max_strain": 0.02, "color": "#B87333", "type": "metal", "grain_size": "nano",   "poisson": 0.34, "n": 0.05, "has_plateau": False, "soft": 0.10},
        "Nitinol (NiTi)":         {"name": "Nitinol",   "E": 50000,  "YS": 400, "UTS": 1000,"max_strain": 0.08, "color": "#4682B4", "type": "superelastic", "poisson": 0.33},
        "Alumina (Al2O3)":        {"name": "Alumina",   "E": 370000, "YS": 260, "UTS": 260, "max_strain": 0.0007,"color": "#F5F5DC","type": "ceramic", "poisson": 0.22},
        "Zirconia (ZrO2)":        {"name": "Zirconia",  "E": 210000, "YS": 800, "UTS": 800, "max_strain": 0.004, "color": "#FFF8DC","type": "ceramic", "poisson": 0.30},
        "PEEK (Polymer)":         {"name": "PEEK",      "E": 3600,   "YS": 100, "UTS": 100, "max_strain": 0.20,  "color": "#F5DEB3","type": "polymer", "poisson": 0.40},
        "Natural Rubber":         {"name": "Natural Rubber","E": 20, "YS": 5,   "UTS": 25,  "max_strain": 6.0,   "color": "#2E8B57","type": "elastomer", "poisson": 0.499},
        "Carbon Nanotube (SWCNT)":{"name": "CNT",       "E": 1000000,"YS": 60000,"UTS": 63000,"max_strain": 0.10, "color": "#1a1a1a","type": "cnt", "grain_size": "nano", "poisson": 0.28},
        "Spider Silk (Dragline)": {"name": "Spider Silk","E": 10000, "YS": 200, "UTS": 1300,"max_strain": 0.30,  "color": "#F0EBD8","type": "biopolymer", "poisson": 0.40},
    }

    col_ui, col_sim = st.columns([1, 5])
    with col_ui:
        st.subheader("Control Panel")
        selected_mat_key = st.selectbox("Select Material", list(materials.keys()), key="t1_mat")
        speed_multiplier = st.slider("Testing Speed", 0.5, 3.0, 1.0, 0.5, key="t1_speed")
        show_offset = st.toggle("📐 Show 0.2% Offset Yield Construction", value=False, key="t1_offset")
        mat = materials[selected_mat_key]
        st.divider()
        ys_disp = mat['YS'] if mat['type'] not in ['ceramic', 'elastomer'] else 'N/A (brittle/hyperelastic)'
        st.markdown(f"**E (Initial):** {mat['E']:,} MPa  \n**YS:** {ys_disp} MPa  \n**UTS:** {mat['UTS']:,} MPa  \n**Max Strain:** {mat['max_strain'] * 100:.2f}%  \n**Poisson ν:** {mat['poisson']}")
        
        if show_offset and mat['type'] in ['metal', 'polymer', 'biopolymer']:
            st.info(r"""
            **0.2 % Offset Method (ISO 6892-1 / ASTM E8)**
            1. Measure the elastic slope **E** through the origin.
            2. Draw a parallel line shifted by **$\varepsilon$ = 0.002** (0.2 %).
            3. The stress at intersection with the $\sigma$-$\varepsilon$ curve is the **proof stress Rp0.2**.
            """)
        if mat['type'] == 'superelastic':
            st.info("🔁 Nitinol test loads to max strain then **unloads**, drawing the full superelastic hysteresis loop.")
        if mat['type'] == 'cnt':
            st.info("⚛️ CNT: linear-elastic to brittle fracture at very high strain. E ~ 1 TPa.")
        if mat['type'] == 'biopolymer':
            st.info("🕸️ Spider silk: yield + J-curve hardening from β-sheet crystals locking the amorphous matrix.")

    html_code_1 = f"""
    <!DOCTYPE html><html><head><style>
        body {{ font-family: sans-serif; color: white; background: #0e1117; margin: 0; padding: 10px; }}
        .dashboard {{ display: flex; justify-content: space-between; margin-bottom: 10px; background: #262730; padding: 15px; border-radius: 8px; }}
        .metric {{ text-align: center; }} .value {{ font-size: 20px; font-weight: bold; color: #4CAF50; }} .label {{ font-size: 11px; color: #aaa; text-transform: uppercase; }}
        .container {{ display: flex; gap: 15px; height: 600px; }}
        .canvas-wrapper {{ background: #1e1e1e; border-radius: 8px; position: relative; overflow: hidden; border: 1px solid #444; }}
        #specimenWrapper, #microWrapper {{ flex: 1; }} #graphWrapper {{ flex: 1.5; }}
        canvas {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: block; }}
        .panel-title {{ position: absolute; top: 10px; left: 10px; z-index: 10; font-size: 12px; color: #ddd; font-weight: bold; background: rgba(0,0,0,0.7); padding: 5px; border-radius: 4px; }}
        .btn {{ background: #FF4B4B; color: white; border: none; padding: 10px; border-radius: 4px; cursor: pointer; font-weight: bold; width: 100%; margin-bottom: 10px; text-transform: uppercase; }}
    </style></head><body>
        <button id="startBtn1" class="btn">🚀 Start Tensile Test</button>
        <div class="dashboard">
            <div class="metric"><div class="label">Strain (\u03B5)</div><div class="value" id="val_strain1">0.0000</div></div>
            <div class="metric"><div class="label">Stress (\u03C3)</div><div class="value" id="val_stress1">0.0 MPa</div></div>
            <div class="metric"><div class="label">Tangent E (init)</div><div class="value" style="color:#FFD700;">{mat['E']:,} MPa</div></div>
            <div class="metric"><div class="label">Secant E (live)</div><div class="value" id="val_mod1" style="color:#FFA500;">{mat['E']:,} MPa</div></div>
            <div class="metric"><div class="label">Min Area</div><div class="value" id="val_area1">25.00 mm²</div></div>
            <div class="metric" id="offsetMetric" style="display:{'block' if show_offset and mat['type'] in ['metal','polymer','biopolymer'] else 'none'};">
                <div class="label">0.2% Offset YS</div><div class="value" id="val_offset" style="color:#00FFFF;">--</div>
            </div>
        </div>
        <div class="container">
            <div class="canvas-wrapper" id="specimenWrapper"><div class="panel-title">Macro: Dog-Bone</div><canvas id="specimenCanvas1"></canvas></div>
            <div class="canvas-wrapper" id="microWrapper"><div class="panel-title">Micro: Physics</div><canvas id="microCanvas1"></canvas></div>
            <div class="canvas-wrapper" id="graphWrapper"><div class="panel-title">Stress-Strain Curve</div><canvas id="graphCanvas1"></canvas></div>
        </div>
        <script>
            const mat = {json.dumps(mat)}; const speed = {speed_multiplier}; const showOffset = {json.dumps(show_offset)};
            let run = false; let strain = 0; let hist = []; let dislocs = [];
            let phase = "loading"; let peakStrain = 0;
            const L0 = 50.0; const W0 = 12.5; const T0 = 2.0;

            function widthAtStrain(eps) {{
                if(eps <= 0) return W0;
                return W0 * Math.pow(1 + eps, -mat.poisson);
            }}

            // ============================================================
            // CONSTITUTIVE LAW — physics-corrected σ(ε) for every class
            // ============================================================
            function getS(e, ph, peak) {{
                ph = ph || "loading"; peak = (peak === undefined) ? 0 : peak;

                if(mat.type === "ceramic") return e >= mat.max_strain ? 0 : e * mat.E;
                if(mat.type === "cnt") return e >= mat.max_strain ? 0 : e * mat.E;

                if(mat.type === "superelastic") {{
                    const eyA   = mat.YS / mat.E;
                    const platL = 0.05;
                    const platE = eyA + platL;
                    const Em    = (mat.UTS - mat.YS) / Math.max(1e-4, mat.max_strain - platE);
                    const sigF  = mat.YS;
                    const sigR  = mat.YS * 0.75;

                    function fwd(x) {{
                        if(x <= 0)     return 0;
                        if(x <= eyA)   return x * mat.E;
                        if(x <= platE) return sigF;
                        return Math.min(mat.UTS, sigF + (x - platE) * Em);
                    }}
                    if(ph === "loading") return fwd(e);

                    const peakStress = fwd(peak);
                    const eRevElEnd  = peak - (peakStress - sigR) / Em;
                    const eRevPlEnd  = sigR / mat.E;

                    if(e >= eRevElEnd) return Math.max(sigR, peakStress - (peak - e) * Em);
                    if(e >= eRevPlEnd) return sigR;
                    return Math.max(0, e * mat.E);
                }}

                if(mat.type === "elastomer") {{
                    const lam    = 1 + Math.min(e, mat.max_strain);
                    const lamMax = 1 + mat.max_strain;
                    const f      = lam - 1/(lam*lam);
                    const fMax   = lamMax - 1/(lamMax*lamMax);
                    const beta   = 1 - 3*mat.UTS / (mat.E * fMax);
                    const betaC  = Math.max(-1, Math.min(1, beta));
                    return (mat.E / 3) * f * (1 - betaC * (lam - 1)/(lamMax - 1));
                }}

                if(mat.type === "biopolymer") {{
                    if(e >= mat.max_strain) return 0;
                    const eY = mat.YS / mat.E;
                    if(e <= eY) return e * mat.E;
                    const r = (e - eY) / (mat.max_strain - eY);
                    return mat.YS + (mat.UTS - mat.YS) * (0.10*r + 0.20*Math.pow(r,2) + 0.70*Math.pow(r,4));
                }}

                if(mat.type === "polymer") {{
                    const eY = mat.YS / mat.E;
                    if(e <= eY) return e * mat.E;
                    const ydrop   = mat.YS * 0.85;
                    const drawEnd = mat.max_strain * 0.75;
                    if(e <= drawEnd) {{
                        const t = (e - eY) / (drawEnd - eY);
                        if(t < 0.15) return mat.YS - (mat.YS - ydrop) * (t / 0.15);
                        return ydrop + (mat.UTS - ydrop) * (t - 0.15) / 0.85;
                    }}
                    return mat.UTS;
                }}

                const eY     = mat.YS / mat.E;
                if(e <= eY) return e * mat.E;
                const platEnd = mat.has_plateau ? eY * 8 : eY;
                if(mat.has_plateau && e <= platEnd) return mat.YS;

                const eUts = Math.max(platEnd + 1e-4, mat.max_strain * 0.6);

                if(e <= eUts) {{
                    const n = mat.n || 0.2;
                    const r = (e - platEnd) / (eUts - platEnd);
                    return Math.min(mat.UTS, mat.YS + (mat.UTS - mat.YS) * Math.pow(Math.max(0, r), n));
                }}

                const soft = (mat.soft === undefined) ? 0.25 : mat.soft;
                const t = (e - eUts) / (mat.max_strain - eUts);
                return Math.max(0, mat.UTS * (1 - soft * t * t));
            }}

            // ============================================================
            // 0.2% OFFSET YIELD — binary search on loading curve
            // ============================================================
            function computeOffsetYield() {{
                if(mat.type === "ceramic" || mat.type === "elastomer" || mat.type === "cnt" || mat.type === "superelastic") return null;
                let lo = 0.002, hi = mat.max_strain;
                // Verify intersection exists
                if(getS(hi, "loading", 0) > mat.E * (hi - 0.002)) return null;
                for(let i=0; i<40; i++) {{
                    const mid = (lo + hi) / 2;
                    if(getS(mid, "loading", 0) > mat.E * (mid - 0.002)) lo = mid;
                    else hi = mid;
                }}
                const eY = (lo + hi) / 2;
                return {{ e: eY, s: getS(eY, "loading", 0) }};
            }}
            const offsetYield = showOffset ? computeOffsetYield() : null;
            if(offsetYield && document.getElementById('val_offset')) {{
                document.getElementById('val_offset').innerText = offsetYield.s.toFixed(1) + " MPa";
            }}

            // ============================================================
            // MICRO INIT
            // ============================================================
            function initMicro() {{
                dislocs = [];
                if(mat.type === "metal") {{
                    const n = (mat.grain_size === "nano") ? 60 : (mat.grain_size === "small" ? 35 : 25);
                    for(let i=0; i<n; i++) dislocs.push({{ x: Math.random()*400, y: Math.random()*400, a:(Math.random()>0.5?45:-45)*Math.PI/180, act:false, spd:0.5+Math.random(), start:(mat.YS/mat.E) + Math.random()*mat.max_strain*0.2 }});
                }}
            }}

            // ============================================================
            // GRAPH
            // ============================================================
            function drawGraph() {{
                const c = document.getElementById('graphCanvas1'); const ctx = c.getContext('2d');
                c.width = c.parentElement.clientWidth; c.height = c.parentElement.clientHeight;
                ctx.clearRect(0,0,c.width,c.height);

                const px = 70, py = 50, pr = 80, pt = 40;
                const w = c.width - px - pr; const h = c.height - py - pt;
                const maxE = mat.max_strain * 1.15;
                const maxS = mat.UTS * 1.30;
                const gX = (v) => px + (v/maxE)*w;
                const gY = (v) => c.height - py - (v/maxS)*h;

                ctx.strokeStyle='#888'; ctx.lineWidth=2; ctx.beginPath();
                ctx.moveTo(px,pt); ctx.lineTo(px,c.height-py); ctx.lineTo(c.width-pr,c.height-py); ctx.stroke();

                ctx.fillStyle='#aaa'; ctx.font='11px sans-serif'; ctx.textAlign='right';
                for(let i=0;i<=5;i++) {{ const v=(maxS/5)*i; const y=gY(v); ctx.fillText(Math.round(v),px-10,y+4); ctx.strokeStyle='#333'; ctx.beginPath(); ctx.moveTo(px,y); ctx.lineTo(c.width-pr,y); ctx.stroke(); }}
                ctx.save(); ctx.translate(20,c.height/2); ctx.rotate(-Math.PI/2); ctx.textAlign='center'; ctx.fillText('Stress (MPa)',0,0); ctx.restore();

                ctx.textAlign='center';
                for(let i=0;i<=5;i++) {{ const v=(maxE/5)*i; const x=gX(v); ctx.fillText(v.toFixed(3),x,c.height-py+20); ctx.strokeStyle='#333'; ctx.beginPath(); ctx.moveTo(x,c.height-py); ctx.lineTo(x,pt); ctx.stroke(); }}
                ctx.fillText('Strain (\u03B5)',px+w/2,c.height-10);

                // --- 0.2% Offset Construction ---
                if(showOffset && offsetYield) {{
                    const eElEnd = Math.min(maxE, maxS / mat.E);
                    const eOffEnd = Math.min(maxE, maxS / mat.E + 0.002);
                    
                    // Elastic line
                    ctx.strokeStyle='rgba(255,215,0,0.6)'; ctx.lineWidth=2; ctx.setLineDash([3,3]);
                    ctx.beginPath(); ctx.moveTo(gX(0), gY(0)); ctx.lineTo(gX(eElEnd), gY(mat.E * eElEnd)); ctx.stroke();
                    
                    // Offset line
                    ctx.strokeStyle='rgba(255,165,0,0.6)';
                    ctx.beginPath(); ctx.moveTo(gX(0.002), gY(0)); ctx.lineTo(gX(eOffEnd), gY(mat.E * (eOffEnd - 0.002))); ctx.stroke();
                    ctx.setLineDash([]);
                    
                    // Intersection dot
                    ctx.fillStyle='#00FFFF'; ctx.beginPath();
                    ctx.arc(gX(offsetYield.e), gY(offsetYield.s), 6, 0, Math.PI*2); ctx.fill();
                    ctx.strokeStyle='#00FFFF'; ctx.lineWidth=2; ctx.stroke();
                    
                    // Horizontal guide to Y-axis
                    ctx.strokeStyle='rgba(0,255,255,0.4)'; ctx.setLineDash([4,4]); ctx.lineWidth=1;
                    ctx.beginPath(); ctx.moveTo(gX(offsetYield.e), gY(offsetYield.s)); ctx.lineTo(px, gY(offsetYield.s)); ctx.stroke();
                    ctx.setLineDash([]);
                    
                    // Labels
                    ctx.fillStyle='rgba(255,215,0,0.9)'; ctx.textAlign='left'; ctx.font='10px sans-serif';
                    ctx.fillText('E (elastic)', gX(eElEnd)+4, gY(mat.E * eElEnd));
                    ctx.fillStyle='rgba(255,165,0,0.9)';
                    ctx.fillText('0.2% offset', gX(eOffEnd)+4, gY(mat.E * (eOffEnd - 0.002)));
                    ctx.fillStyle='#00FFFF'; ctx.textAlign='right';
                    ctx.fillText(`Rp0.2 = ${{offsetYield.s.toFixed(1)}} MPa`, px - 8, gY(offsetYield.s) + 4);
                }}

                if(mat.type !== "ceramic" && mat.type !== "cnt" && mat.type !== "elastomer") {{
                    ctx.strokeStyle='rgba(255,215,0,0.35)'; ctx.setLineDash([4,4]);
                    ctx.beginPath(); ctx.moveTo(px, gY(mat.YS)); ctx.lineTo(c.width-pr, gY(mat.YS)); ctx.stroke();
                    ctx.fillStyle='rgba(255,215,0,0.7)'; ctx.textAlign='left'; ctx.fillText('YS', c.width-pr+5, gY(mat.YS)+4);
                    ctx.setLineDash([]);
                }}
                ctx.strokeStyle='rgba(255,75,75,0.35)'; ctx.setLineDash([4,4]);
                ctx.beginPath(); ctx.moveTo(px, gY(mat.UTS)); ctx.lineTo(c.width-pr, gY(mat.UTS)); ctx.stroke();
                ctx.fillStyle='rgba(255,75,75,0.7)'; ctx.textAlign='left'; ctx.fillText('UTS', c.width-pr+5, gY(mat.UTS)+4);
                ctx.setLineDash([]);

                if(hist.length > 0) {{
                    ctx.strokeStyle='#FF4B4B'; ctx.lineWidth=3; ctx.beginPath();
                    ctx.moveTo(gX(hist[0].x), gY(hist[0].y));
                    for(let i=1;i<hist.length;i++) ctx.lineTo(gX(hist[i].x), gY(hist[i].y));
                    ctx.stroke();
                    ctx.fillStyle='#fff'; ctx.beginPath();
                    ctx.arc(gX(hist[hist.length-1].x), gY(hist[hist.length-1].y), 5, 0, Math.PI*2); ctx.fill();
                }}
            }}

            // ============================================================
            // MACRO
            // ============================================================
            function drawMacro() {{
                const c = document.getElementById('specimenCanvas1'); const ctx = c.getContext('2d');
                c.width = c.parentElement.clientWidth; c.height = c.parentElement.clientHeight;
                ctx.clearRect(0,0,c.width,c.height);

                const frac = (mat.type === "superelastic") ? false : (strain >= mat.max_strain && phase !== "unloading");
                const dE = Math.min(strain, mat.max_strain);

                const W = widthAtStrain(dE);
                const L = L0 * (1 + dE);
                const canNeck = (mat.type === "metal" || mat.type === "polymer" || mat.type === "biopolymer");
                const neckOnset = mat.max_strain * 0.6;
                const neck = (canNeck && dE > neckOnset) ? W * 0.4 * ((dE - neckOnset) / (mat.max_strain - neckOnset)) : 0;

                const maxL = L0 * (1 + mat.max_strain);
                const sc = c.height / (maxL + 80);
                const cx = c.width/2, cy = c.height/2;

                let minW = W;
                ctx.beginPath();
                for(let y=-L/2; y<=L/2; y+=L/60) {{
                    let cW = (W/2) - (neck * Math.exp(-(y*y)/(L0*0.2)));
                    if(Math.abs(y) > L/2 - L0*0.1) cW = W0*0.9;
                    let py = cy + y*sc; if(frac && y>0) py += 10;
                    if(y === -L/2) ctx.moveTo(cx + cW*sc, py); else ctx.lineTo(cx + cW*sc, py);
                    if(cW*2 < minW) minW = cW*2;
                }}
                for(let y=L/2; y>=-L/2; y-=L/60) {{
                    let cW = (W/2) - (neck * Math.exp(-(y*y)/(L0*0.2)));
                    if(Math.abs(y) > L/2 - L0*0.1) cW = W0*0.9;
                    let py = cy + y*sc; if(frac && y>0) py += 10;
                    ctx.lineTo(cx - cW*sc, py);
                }}
                ctx.closePath(); ctx.fillStyle = mat.color; ctx.fill();

                ctx.save(); ctx.clip();
                const eY = (mat.YS && mat.E && mat.type !== "ceramic" && mat.type !== "cnt") ? mat.YS/mat.E : 0;
                const showHeat = (dE > eY) && (mat.type !== "ceramic") && (mat.type !== "cnt") && (mat.type !== "superelastic");
                if(showHeat) {{
                    const pp = Math.min(1.0, (dE - eY)/(mat.max_strain - eY));
                    const heatHalfH = (neck > 0) ? (L0*0.15)*sc : (L*0.25)*sc;
                    const grd = ctx.createLinearGradient(0, cy - heatHalfH, 0, cy + heatHalfH);
                    grd.addColorStop(0, "transparent");
                    grd.addColorStop(0.5, `rgba(255, 69, 0, ${{pp*0.6}})`);
                    grd.addColorStop(1, "transparent");
                    ctx.fillStyle = grd; ctx.fillRect(cx - W0*sc, cy - heatHalfH, W0*2*sc, 2*heatHalfH);
                }}
                ctx.restore();
                ctx.strokeStyle="white"; ctx.lineWidth=1; ctx.stroke();

                ctx.fillStyle='#2F4F4F';
                const gW = W0*2.2*sc, gH = 40;
                ctx.fillRect(cx - gW/2, cy - (L/2)*sc - gH + 5, gW, gH);
                ctx.fillRect(cx - gW/2, cy + (L/2)*sc + (frac?10:0) - 5, gW, gH);

                const curS = getS(strain, phase, peakStrain);
                const curMod = (strain > 1e-4 && !frac) ? (curS / strain).toFixed(0) : (frac ? "0" : mat.E);
                document.getElementById('val_strain1').innerText = strain.toFixed(4);
                document.getElementById('val_stress1').innerText = frac ? "Fractured" : (curS.toFixed(1) + " MPa");
                document.getElementById('val_mod1').innerText  = curMod + " MPa";
                const area = frac ? 0 : T0 * minW * minW / W0;
                document.getElementById('val_area1').innerText = area.toFixed(2) + " mm²";
            }}

            // ============================================================
            // MICRO
            // ============================================================
            function drawMicro() {{
                const c = document.getElementById('microCanvas1'); const ctx = c.getContext('2d');
                c.width = c.parentElement.clientWidth; c.height = c.parentElement.clientHeight;
                const frac = (mat.type === "superelastic") ? false : (strain >= mat.max_strain && phase !== "unloading");
                ctx.fillStyle='#111'; ctx.fillRect(0,0,c.width,c.height);

                if(mat.type === "metal" || mat.type === "superelastic") {{
                    const gs = (mat.grain_size === "nano") ? 30 : (mat.grain_size === "small") ? 60 : 80;
                    ctx.strokeStyle='#444'; ctx.lineWidth=1.5;
                    ctx.beginPath();
                    for(let x=-gs; x<c.width+gs; x+=gs) for(let y=-gs; y<c.height+gs; y+=gs) {{
                        const off = (Math.floor(y/gs)%2===0) ? 0 : gs/2;
                        ctx.rect(x-off, y, gs, gs);
                    }}
                    ctx.stroke();

                    if(mat.type === "metal") {{
                        ctx.strokeStyle='#FFeb3b'; ctx.lineWidth=2;
                        dislocs.forEach(d => {{
                            if(strain > d.start && !frac) d.act = true;
                            if(d.act) {{
                                d.x += Math.cos(d.a) * d.spd; d.y += Math.sin(d.a) * d.spd;
                                const lx = ((d.x % gs) + gs) % gs, ly = ((d.y % gs) + gs) % gs;
                                if(lx < 3 || ly < 3 || lx > gs-3 || ly > gs-3) d.spd *= 0.92;
                            }}
                            ctx.save();
                            ctx.translate(((d.x % c.width)+c.width)%c.width, ((d.y % c.height)+c.height)%c.height);
                            ctx.rotate(d.a);
                            ctx.beginPath(); ctx.moveTo(-6,0); ctx.lineTo(6,0); ctx.moveTo(0,0); ctx.lineTo(0,10); ctx.stroke();
                            ctx.restore();
                        }});
                    }} else {{
                        const r = strain / mat.max_strain;
                        const bandY = (phase === "loading" ? r : (peakStrain/mat.max_strain)*(strain/peakStrain)) * c.height;
                        ctx.fillStyle = (phase === "loading") ? "rgba(255,140,0,0.25)" : "rgba(70,130,180,0.30)";
                        ctx.fillRect(0, 0, c.width, bandY);
                        ctx.fillStyle = "rgba(255,255,255,0.85)"; ctx.font = "12px sans-serif"; ctx.textAlign = "left";
                        ctx.fillText(phase === "loading" ? "Austenite → Martensite" : "Martensite → Austenite", 10, c.height - 12);
                    }}
                }}

                else if(mat.type === "ceramic") {{
                    const gs = 35;
                    ctx.strokeStyle='#555'; ctx.lineWidth=1;
                    ctx.beginPath();
                    for(let x=0; x<c.width; x+=gs) for(let y=0; y<c.height; y+=gs) {{
                        const off = (Math.floor(y/gs)%2===0) ? 0 : gs/2;
                        ctx.moveTo(x-off, y); ctx.lineTo(x-off+gs, y);
                        ctx.moveTo(x-off+gs, y); ctx.lineTo(x-off+gs/2, y+gs);
                        ctx.moveTo(x-off+gs/2, y+gs); ctx.lineTo(x-off, y);
                    }}
                    ctx.stroke();
                    const r = strain/mat.max_strain;
                    if(r > 0.8) {{
                        ctx.strokeStyle = `rgba(255,75,75,${{(r-0.8)*5}})`;
                        ctx.lineWidth = 1.5;
                        for(let i=0; i<6; i++) {{
                            const sx = c.width*0.3 + i*15, sy = c.height*0.5 + Math.sin(i)*20;
                            ctx.beginPath(); ctx.moveTo(sx, sy); ctx.lineTo(sx + Math.cos(i)*10, sy + Math.sin(i)*10); ctx.stroke();
                        }}
                    }}
                }}

                else if(mat.type === "cnt") {{
                    const a = 28;
                    const stretch = 1 + Math.min(strain, mat.max_strain) * 6;
                    ctx.strokeStyle = "#888"; ctx.lineWidth = 1.4;
                    for(let row=-1; row<c.height/(a*stretch)+2; row++) {{
                        for(let col=-1; col<c.width/(a*1.5)+2; col++) {{
                            const cx0 = col * a * 1.5;
                            const cy0 = (row + (col%2 ? 0.5 : 0)) * a * stretch;
                            ctx.beginPath();
                            for(let v=0; v<=6; v++) {{
                                const ang = v*Math.PI/3;
                                const px = cx0 + (a*0.55)*Math.cos(ang);
                                const py = cy0 + (a*0.55)*stretch*Math.sin(ang);
                                if(v===0) ctx.moveTo(px,py); else ctx.lineTo(px,py);
                            }}
                            ctx.stroke();
                        }}
                    }}
                    ctx.fillStyle = "#bbb";
                    for(let row=-1; row<c.height/(a*stretch)+2; row++) {{
                        for(let col=-1; col<c.width/(a*1.5)+2; col++) {{
                            const cx0 = col * a * 1.5;
                            const cy0 = (row + (col%2 ? 0.5 : 0)) * a * stretch;
                            ctx.beginPath(); ctx.arc(cx0, cy0, 1.5, 0, Math.PI*2); ctx.fill();
                        }}
                    }}
                }}

                else if(mat.type === "biopolymer") {{
                    const r = Math.min(1, strain / mat.max_strain);
                    const numCh = 6;
                    for(let i=0; i<numCh; i++) {{
                        const xC = (i + 0.5) * c.width / numCh;
                        ctx.strokeStyle = "#cfc8a8"; ctx.lineWidth = 1.8;
                        let y = 0;
                        while(y < c.height) {{
                            const segLen = 35 * (1 + r*1.8);
                            const amp = 14 * (1 - r*0.92);
                            ctx.beginPath(); ctx.moveTo(xC, y);
                            for(let dy=0; dy<=segLen; dy+=2) {{
                                const wx = xC + amp * Math.sin(dy*0.35 + i);
                                ctx.lineTo(wx, y + dy);
                            }}
                            ctx.stroke();
                            y += segLen;
                            if(y < c.height) {{
                                const blockH = 14;
                                ctx.save();
                                ctx.translate(xC, y + blockH/2);
                                ctx.rotate((1 - r) * 0.4 * (i%2 ? 1 : -1));
                                ctx.fillStyle = "#7a8c5a";
                                ctx.fillRect(-6, -blockH/2, 12, blockH);
                                ctx.strokeStyle = "#4a5a3a"; ctx.lineWidth = 1;
                                ctx.strokeRect(-6, -blockH/2, 12, blockH);
                                ctx.strokeStyle = "rgba(0,0,0,0.4)";
                                for(let h=-blockH/2+2; h<blockH/2; h+=3) {{
                                    ctx.beginPath(); ctx.moveTo(-5, h); ctx.lineTo(5, h); ctx.stroke();
                                }}
                                ctx.restore();
                                y += blockH;
                            }}
                        }}
                    }}
                    ctx.fillStyle = "rgba(255,255,255,0.6)"; ctx.font = "11px sans-serif"; ctx.textAlign = "left";
                    ctx.fillText(`β-sheet crystals + amorphous matrix · alignment ${{(r*100).toFixed(0)}}%`, 10, c.height-10);
                }}

                else if(mat.type === "elastomer" || mat.type === "polymer") {{
                    const r = Math.min(1, strain / mat.max_strain);
                    const amp = 22 * (1 - r*0.95);
                    const ph = r * 4;
                    ctx.strokeStyle = (mat.type === "elastomer") ? "#2E8B57" : "#caa274";
                    ctx.lineWidth = 2.5;
                    for(let i=20; i<c.width; i+=40) {{
                        ctx.beginPath();
                        for(let y=0; y<c.height; y+=4) {{
                            const wx = i + amp * Math.sin(y*0.08 + ph + i*0.01);
                            if(y===0) ctx.moveTo(wx, y); else ctx.lineTo(wx, y);
                        }}
                        ctx.stroke();
                    }}
                    if(mat.type === "elastomer") {{
                        ctx.fillStyle = "rgba(255,255,255,0.6)"; ctx.font = "11px sans-serif"; ctx.textAlign = "left";
                        ctx.fillText(`chain alignment ${{(r*100).toFixed(0)}}%  ·  λ = ${{(1+strain).toFixed(2)}}`, 10, c.height-10);
                    }}
                }}

                if(frac) {{
                    ctx.strokeStyle='#FF4B4B'; ctx.lineWidth=5;
                    ctx.beginPath(); ctx.moveTo(c.width/2, 0);
                    ctx.lineTo(c.width/2-12, c.height*0.4); ctx.lineTo(c.width/2+18, c.height*0.7); ctx.lineTo(c.width/2, c.height);
                    ctx.stroke();
                    ctx.fillStyle="rgba(0,0,0,0.5)"; ctx.fillRect(0,0,c.width,c.height);
                }}
            }}

            // ============================================================
            // MAIN LOOP
            // ============================================================
            function loop() {{
                if(!run) return;

                let inc = (mat.max_strain/500) * speed;
                if(mat.type !== "ceramic" && mat.type !== "cnt" && mat.type !== "elastomer" && strain < (mat.YS/mat.E)) inc *= 0.3;

                if(mat.type === "superelastic") {{
                    if(phase === "loading") {{
                        strain += inc;
                        if(strain >= mat.max_strain) {{ strain = mat.max_strain; peakStrain = strain; phase = "unloading"; }}
                    }} else if(phase === "unloading") {{
                        strain -= inc;
                        if(strain <= 0) {{
                            strain = 0;
                            hist.push({{x:strain, y:getS(strain, phase, peakStrain)}});
                            drawMacro(); drawMicro(); drawGraph();
                            document.getElementById('startBtn1').innerText="CYCLE COMPLETE - RESET";
                            run = false; return;
                        }}
                    }}
                }} else {{
                    strain += inc;
                    if(strain >= mat.max_strain) {{
                        strain = mat.max_strain;
                        hist.push({{x:strain, y:getS(strain, phase, peakStrain)}});
                        drawMacro(); drawMicro(); drawGraph();
                        document.getElementById('startBtn1').innerText="TEST COMPLETE - RESET";
                        run=false; return;
                    }}
                }}

                hist.push({{x:strain, y:getS(strain, phase, peakStrain)}});
                drawMacro(); drawMicro(); drawGraph();
                requestAnimationFrame(loop);
            }}

            document.getElementById('startBtn1').addEventListener('click', () => {{
                const btn = document.getElementById('startBtn1');
                if(btn.innerText.includes("RESET")) {{
                    strain=0; hist=[]; phase="loading"; peakStrain=0;
                    initMicro(); drawMacro(); drawMicro(); drawGraph();
                    btn.innerText = "🚀 Start Tensile Test";
                    return;
                }}
                run=true; loop();
            }});

            initMicro(); drawMacro(); drawMicro(); drawGraph();
            window.addEventListener('resize', () => {{ if(!run) {{ drawMacro(); drawMicro(); drawGraph(); }} }});
        </script>
    </body></html>
    """
    with col_sim:
        components.html(html_code_1, height=750, scrolling=False)

# ==========================================
# TAB 3: DISLOCATIONS & DEFECTS
# ==========================================
with tab3:
    st.header("Dislocations & Lattice Defects")
    st.markdown(r"""
    Real crystals are *never* geometrically perfect. They contain **defects**, and these
    defects — not the bonds — control plastic deformation. The strength of a real crystal
    is **two to four orders of magnitude smaller** than the theoretical strength estimated
    from breaking all bonds at once. Dislocations explain that gap.

    ### 1. Point defects (0-D)
    * **Vacancy** — a missing atom. Concentration is thermally activated:
      $c_v = \exp(-Q_v/k_BT)$.
    * **Interstitial** — an extra atom squeezed between lattice sites
      (e.g. C in BCC iron → controls steel hardness).
    * **Substitutional impurity** — a foreign atom replacing a host atom
      (e.g. Zn in Cu → brass).

    ### 2. Line defects — dislocations (1-D)
    A **dislocation** is a line along which the regular crystal structure is disrupted.
    Two pure types exist:

    * **Edge dislocation** — an extra half-plane of atoms is wedged into the lattice.
      The line is *perpendicular* to its **Burgers vector** $\mathbf{b}$
      (slip direction).
    * **Screw dislocation** — the lattice is helically twisted around the dislocation
      line. The line is *parallel* to $\mathbf{b}$.
    * **Mixed** — most real dislocations are mixed edge–screw character.

    The Burgers vector $\mathbf{b}$ is found by drawing a closed atomic-step loop in a
    perfect crystal and the same loop in a crystal containing the dislocation.
    The **closure failure** is $\mathbf{b}$. Its magnitude is one lattice spacing in metals.

    When stress is applied, dislocations **glide** along close-packed planes
    in close-packed directions — this is **slip**. Slip is the physical mechanism of
    plastic deformation in metals, and it is the reason real metals yield at $\sim E/100$
    rather than $E/10$ (the theoretical "ideal" strength).
    """)

    # Real matplotlib diagram of an edge dislocation glide step
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.6), gridspec_kw={'wspace': 0.25})

    def draw_lattice_panel(ax, half_plane_col, b_arrow=False, exited=False, title=""):
        ax.set_xlim(-0.5, 7.5); ax.set_ylim(-0.7, 5.5)
        ax.set_aspect('equal'); ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(title, fontsize=10)
        for sp in ax.spines.values(): sp.set_color("#444")

        # Lower 3 perfect rows (j = 0,1,2) — undisturbed
        for i in range(8):
            for j in range(3):
                ax.plot(i, j, 'o', color="#cccccc", markersize=10, mec='#222', mew=0.8)

        if not exited:
            # Upper rows are mildly distorted around the dislocation
            for i in range(8):
                for j in range(3, 5):
                    if i < half_plane_col:
                        x = i - 0.05*(j-2.5)
                    elif i > half_plane_col:
                        x = i + 0.05*(j-2.5)
                    else:
                        x = i
                    ax.plot(x, j, 'o', color="#cccccc", markersize=10, mec='#222', mew=0.8)
            # The extra half-plane: red atoms above the lattice, terminating at j=3 (the core)
            ax.plot(half_plane_col, 3.5, 'o', color="#FF4B4B", markersize=10, mec='#222', mew=0.8)
            ax.plot(half_plane_col, 4.5, 'o', color="#FF4B4B", markersize=10, mec='#222', mew=0.8)
            ax.plot([half_plane_col, half_plane_col], [3.5, 4.5], '-', color="#FF4B4B", lw=1.5)
            # ⊥ symbol AT THE DISLOCATION CORE (not at the bottom)
            ax.text(half_plane_col, 3.0, "⊥", color="#FF4B4B", fontsize=22,
                    ha='center', va='center', fontweight='bold')
        else:
            # Surface step: upper rows are flat except for an offset of one Burgers-vector
            for i in range(8):
                for j in range(3, 5):
                    # right side has shifted left by one column compared to bottom rows
                    x = i + (1 if i >= 4 else 0) * 0
                    ax.plot(i, j, 'o', color="#cccccc", markersize=10, mec='#222', mew=0.8)
            # Show the step on the top surface (a missing atom at the right end of row 4)
            # i.e., one extra atom on the top-right edge
            ax.plot(7.5, 4, 'o', color="#FFD700", markersize=10, mec='#222', mew=0.8)
            ax.annotate("step = $\\mathbf{b}$",
                        xy=(7.5, 4), xytext=(5.4, 5.0),
                        color="#FFD700", fontsize=10,
                        arrowprops=dict(arrowstyle="->", color="#FFD700", lw=1.2))

        if b_arrow:
            ax.annotate("", xy=(half_plane_col+1.0, 3.0),
                        xytext=(half_plane_col+0.15, 3.0),
                        arrowprops=dict(arrowstyle="->", color="#FFD700", lw=2.2))
            ax.text(half_plane_col+0.55, 2.55, r"$\mathbf{b}$", color="#FFD700",
                    fontsize=14, ha='center', fontweight='bold')

        # Shear sense τ arrows
        ax.annotate("", xy=(7.0, 4.7), xytext=(5.2, 4.7),
                    arrowprops=dict(arrowstyle="->", color="#4CAF50", lw=1.8))
        ax.annotate("", xy=(0.0, 0.3), xytext=(1.8, 0.3),
                    arrowprops=dict(arrowstyle="->", color="#4CAF50", lw=1.8))
        ax.text(7.2, 4.7, r"$\tau$", color="#4CAF50", fontsize=12, va='center')

    draw_lattice_panel(axes[0], 2, b_arrow=False, exited=False,
                       title="(a)  Edge dislocation in lattice")
    draw_lattice_panel(axes[1], 4, b_arrow=True,  exited=False,
                       title="(b)  Dislocation glides by $\\mathbf{b}$")
    draw_lattice_panel(axes[2], 7, b_arrow=False, exited=True,
                       title="(c)  Surface step left after exit")

    fig.suptitle("Edge-dislocation glide: how plastic shear advances atom by atom",
                 color="#ffffff", fontsize=12, y=1.02)
    st.pyplot(fig, width="stretch")
    plt.close(fig)

    st.markdown(r"""
    The figure shows why slip costs so little stress: only the atoms *along the dislocation
    line* need to move at any instant — not an entire plane of bonds at once.
    Each pass of a dislocation produces one Burgers-vector step on the surface.

    ### 3. Planar defects (2-D)
    * **Grain boundaries** — interfaces between mis-oriented crystals (treated in detail
      in the Hall–Petch tab).
    * **Twin boundaries** — special, low-energy mirror-symmetry boundaries; common in FCC
      metals with low stacking-fault energy.
    * **Stacking faults** — local errors in the stacking sequence
      (e.g. ABC**A**BC instead of ABC ABC in FCC).
    """)

    with st.expander("📚 Theory deep-dive: slip systems, Frank–Read sources, and the four strengthening mechanisms"):
        st.markdown(r"""
**Slip systems and Schmid's law.** Slip occurs only on specific
close-packed *planes* in close-packed *directions*; together they form a **slip system**.

| Crystal | Slip plane | Slip direction | # systems |
|---|---|---|---|
| FCC (Cu, Al, Ni, $\gamma$-Fe) | {111} | <110> | 12 |
| BCC ($\alpha$-Fe, W, Mo) | {110}, {112}, {123} | <111> | 48 |
| HCP (Mg, Ti, Zn, Co) | {0001} basal | <11$\bar 2$0> | 3 |

The **resolved shear stress** on a slip system is given by Schmid's law:
$\tau_R = \sigma\,\cos\phi\,\cos\lambda$, where $\phi$ is the angle between the loading
axis and the slip-plane normal, $\lambda$ between the loading axis and the slip direction.
The product $\cos\phi\cos\lambda$ is the **Schmid factor** (max 0.5).
Slip starts on the system with the highest Schmid factor when $\tau_R$ reaches the
**critical resolved shear stress** $\tau_{CRSS}$.

The 12 systems of FCC explain its excellent ductility; the 3 basal systems of HCP
explain why pure Mg or Ti are comparatively brittle at room temperature.

**Frank–Read source — how dislocations multiply.** A dislocation segment pinned at two
points bows out under shear stress, eventually closing on itself and emitting a new
dislocation loop. The critical stress is $\tau_{FR} \approx Gb/L$ where $L$ is the
distance between pins. This is why a metal that has been plastically deformed contains
*more* dislocations than the virgin material — and is harder.

**Strain energy of a dislocation.** Per unit length:
$U_{disl} \approx \tfrac{1}{2} G b^2$
This is why slip prefers small Burgers vectors (closest-packed directions).

**The four strengthening mechanisms** (all work by impeding dislocation motion):
1. **Grain-size strengthening** — Hall–Petch (see next tab).
2. **Strain (work) hardening** — dislocation tangles. $\sigma_y \propto G b \sqrt{\rho}$
   (Taylor's relation).
3. **Solid-solution strengthening** — solute atoms create local lattice strain.
   Effect $\propto \sqrt{c}$ for substitutional, $\propto c^{2/3}$ for interstitial.
4. **Precipitation/dispersion strengthening** — second-phase particles force dislocations
   to either bow around them (Orowan, $\tau \propto Gb/L$) or shear them.

These four mechanisms are **approximately additive** — the basis of all alloy design.
""")

    with st.expander("🕹️ How to observe defects in this lab"):
        st.markdown("""
This tab is intentionally theory-rich because dislocations are *invisible* on a macroscale.
But you have already seen them in action:

* In **Tab 📈 Stress–Strain**, the *Micro: Physics* panel of every metal shows tiny
  yellow ⊥-symbols moving across the grain — these are dislocations gliding once you
  pass yield.  Watch them slow down when they hit grain boundaries.
* In **Tab 📏 Hall–Petch** you can directly count more dislocations in finer-grained
  microstructures and see their motion stalled by the denser boundary network.
* In **Tab ⚡ Atomic Origin** the lattice canvas shows the *elastic* limit of single
  bonds — but real metals never reach that limit because dislocations let them slip first.

**Exercise.** Open Tab 📈 → run *Aluminium 7075-T6* at speed 0.5×. Pause your eye at
$\\varepsilon \\approx 0.01$ and count the moving ⊥ symbols. Then run *nc-Copper* (nano-grained):
the dislocation count looks higher *but* their motion barely advances — the boundaries
are everywhere. That is exactly why nc-Cu has YS = 750 MPa while a coarse-grained Cu
yields below 100 MPa.
""")

    with st.expander("📐 Worked exercises with formulas — solve these by hand"):
        st.markdown(r"""
The next batch of problems forces you to manipulate the formulas you saw in the deep-dive.
Have a calculator ready.

---

### Exercise 1 — Burgers vector magnitude in FCC and BCC
**FCC** copper slips on $\{111\}\langle 110\rangle$, so $\mathbf{b} = \tfrac{a}{2}\langle 110\rangle$ and $|\mathbf{b}| = a/\sqrt{2}$.

For Cu, $a = 0.3615$ nm.

**Solution.** $|\mathbf{b}|_{Cu} = 0.3615/\sqrt{2} = \mathbf{0.2557\;\text{nm}}$

**BCC** $\alpha$-iron slips on $\{110\}\langle 111\rangle$, so $\mathbf{b} = \tfrac{a}{2}\langle 111\rangle$ and $|\mathbf{b}| = a\sqrt{3}/2$.

For Fe, $a = 0.2866$ nm. **Solution.** $|\mathbf{b}|_{Fe} = 0.2866\times \sqrt{3}/2 = \mathbf{0.2482\;\text{nm}}$

> Both are close to one atomic diameter — slip is always the *shortest* lattice repeat vector,
> because the elastic energy of a dislocation $\propto |\mathbf{b}|^2$.

---

### Exercise 2 — Schmid's law: resolve a tensile stress onto a slip system
A copper single crystal is pulled along $[001]$. Slip is on $(111)[\bar{1}01]$.

**Formula.** $\tau_{RSS} = \sigma\cos\phi\cos\lambda$ where $\phi$ is the angle between the **load**
axis and the **slip plane normal**, $\lambda$ between the load axis and the **slip direction**.

**Geometry.**
- Slip plane normal $(111)$ vs load $[001]$: $\cos\phi = 1/\sqrt{3} = 0.577 \Rightarrow \phi = 54.7^\circ$
- Slip direction $[\bar{1}01]$ vs load $[001]$: $\cos\lambda = 1/\sqrt{2} = 0.707 \Rightarrow \lambda = 45^\circ$
- Schmid factor: $m = \cos\phi\cos\lambda = 0.577 \times 0.707 = \mathbf{0.408}$

If macroscopic yield is at $\sigma_y = 50$ MPa, the resolved (critical) shear stress on this system is

$$\tau_{CRSS} = m\,\sigma_y = 0.408 \times 50 = \mathbf{20.4\;\text{MPa}}$$

> $m_{\max} = 0.5$ corresponds to a slip plane and slip direction both at $45^\circ$ to the load —
> the easiest orientation. Crystals oriented with $m \to 0$ ("hard orientations") need much higher
> stress to slip.

---

### Exercise 3 — Taylor's relation: how much does cold work strengthen?
Cold rolling raises dislocation density from $\rho_0 = 10^{12}\;\text{m}^{-2}$ (annealed) to $\rho_1 = 10^{15}\;\text{m}^{-2}$.
Use $\alpha = 0.3$, $G = 80$ GPa, $b = 0.25$ nm.

**Formula.** $\tau = \alpha G b \sqrt{\rho}$

**Solution.**
- $\tau_0 = 0.3 \times 80\times 10^9 \times 0.25\times 10^{-9} \times \sqrt{10^{12}} = 0.3 \times 20 \times 10^6 = \mathbf{6\;\text{MPa}}$
- $\tau_1 = 0.3 \times 80\times 10^9 \times 0.25\times 10^{-9} \times \sqrt{10^{15}} = 6 \times \sqrt{10^3} = \mathbf{190\;\text{MPa}}$
- **Strengthening contribution:** $\Delta\tau \approx 184$ MPa.

A factor-of-1000 in $\rho$ gives only $\sqrt{1000}\approx 32$× in $\tau$ — that's the square-root law.

---

### Exercise 4 — Orowan looping: spacing controls strength
Particles distributed on a slip plane with mean spacing $L = 100$ nm. $G = 80$ GPa, $b = 0.25$ nm.

**Formula.** $\Delta\tau_{\text{Orowan}} = \dfrac{Gb}{L}$

**Solution.** $\Delta\tau = (80\times 10^9)(0.25\times 10^{-9})/(100\times 10^{-9}) = \mathbf{200\;\text{MPa}}$

**What if you halve the spacing to 50 nm?** $\Delta\tau$ doubles to 400 MPa. This is precisely why
*finer* dispersions of precipitates strengthen more — and why over-aging (which coarsens precipitates)
*weakens* an alloy.

---

### Exercise 5 — Frank–Read source: critical activation stress
A pinned dislocation segment of length $L = 1\;\mu\text{m} = 10^{-6}$ m. $G = 80$ GPa, $b = 0.25$ nm.

**Formula.** Same as Orowan: $\tau_{\text{crit}} = Gb/L$

**Solution.** $\tau_{\text{crit}} = (80\times 10^9)(0.25\times 10^{-9})/10^{-6} = \mathbf{20\;\text{MPa}}$

> Frank–Read sources with **shorter** pinned segments need higher stress to operate — another
> route by which fine microstructure raises strength.

---

### Exercise 6 — Dislocation density from etch-pit count
A polished and etched surface shows 5 × 10⁵ etch pits per cm².
Each pit marks one dislocation intersecting the surface.

**Formula.** $\rho = N_{\text{pits}}/A$

**Solution.** $\rho = 5\times 10^5/\text{cm}^2 = 5\times 10^5/(10^{-4}\,\text{m}^2) = \mathbf{5\times 10^9\;\text{m}^{-2}}$

This is typical of an annealed metal. After cold work, $\rho$ jumps to $10^{14}$–$10^{15}\;\text{m}^{-2}$.
Use Taylor (Ex 3) to confirm the strength jump.

---

### Exercise 7 — Combined strengthening (additive rule)
A copper alloy has the following contributions to yield (each in MPa):
- Friction (Peierls): $\sigma_0 = 20$
- Solid solution (5 % Zn brass-style): $\sigma_{ss} = 60$
- Hall–Petch ($d = 10\,\mu\text{m}$, $k_y = 110$): $\sigma_{HP} = 110/\sqrt{10} = 34.8$
- Forest dislocations ($\rho = 10^{14}\;\text{m}^{-2}$, Taylor with $G=48$ GPa, $b=0.256$ nm, $\alpha=0.3 \Rightarrow \tau=37$ MPa, then $\sigma=2\tau\approx 74$ MPa)

**Formula (linear superposition).** $\sigma_y = \sigma_0 + \sigma_{ss} + \sigma_{HP} + \sigma_{\rho}$

**Solution.** $\sigma_y = 20 + 60 + 34.8 + 74 = \mathbf{189\;\text{MPa}}$

This is roughly the yield strength of half-hard cold-rolled brass — and shows quantitatively
how an alloy designer trades grain refinement, alloying, and cold work to hit a target strength.
""")

    # ---- Hidden bonus exercise (gated) ----
    hidden_exercise(
        key_prefix="t3_bonus",
        title="🔒 Hidden bonus exercise — read the deep-dive expander to unlock",
        gate_question=(
            r"What is the **surname** of the scientist whose relation $\tau = \alpha G b\sqrt{\rho}$ "
            "links flow stress to dislocation density? (One word, English spelling.)"
        ),
        hint="It's also the surname of the scientist who derived the polycrystal averaging factor M ≈ 3.06.",
        accepted_answers=["taylor", "g.i. taylor", "gi taylor", "geoffrey taylor"],
        exercise_md=r"""
### 🏆 Bonus — From Schmid factor to the Taylor factor

In a single crystal pulled along $[001]$, you found in *Worked Exercise 2* that $m = 0.408$
on the $(111)[\bar{1}01]$ system. But a real polycrystal contains **billions of grains**,
each with a different orientation relative to the load. Some grains are well-oriented
($m \to 0.5$, easy slip); others are badly oriented ($m \to 0$, hard slip).

When you average over a random texture, the **Taylor factor** $M = \langle 1/m\rangle$
emerges. For a randomly textured **FCC** polycrystal Taylor's calculation gives $M \approx 3.06$.

**Problem.** Pure annealed nickel has $\tau_{CRSS} \approx 5$ MPa (single-crystal value).

(i) Predict the polycrystalline yield strength using $\sigma_y = M\,\tau_{CRSS}$.

(ii) Compare with the experimental Hall–Petch friction stress $\sigma_0 \approx 50$ MPa for Ni
(see Tab 4 worked exercises). Where does the rest of the strength come from?

---

**Solution.**
- (i) $\sigma_y = 3.06 \times 5 = \mathbf{15.3\;\text{MPa}}$ — the *intrinsic* contribution of polycrystalline averaging.
- (ii) The remaining $50 - 15 \approx \mathbf{35\;\text{MPa}}$ comes from the lattice friction
  (Peierls stress) plus residual forest dislocations even in the annealed state. Together
  these constitute $\sigma_0$.

> **Why $M = 3.06$, not 1/0.5 = 2?** Because no real polycrystal can deform with all grains
> finding their easiest slip system — *strain compatibility* across grain boundaries forces
> several systems to operate simultaneously in each grain. Taylor's 1938 paper showed that
> at least 5 independent slip systems must be active to accommodate an arbitrary plastic strain
> tensor. This raises the average resolved stress required, hence $M > 2$.
""",
    )

# ==========================================
# TAB 4: HALL-PETCH THEORY
# ==========================================
with tab4:
    st.header("The Hall-Petch Effect")
    st.markdown(r"""
    Plastic deformation requires dislocations to move. **Anything that blocks their path
    increases the strength of the material.** A *grain boundary* is a highly effective
    obstacle: when a glide dislocation reaches one, the adjacent grain has its slip
    planes oriented differently, so the dislocation cannot easily continue. Dislocations
    pile up against the boundary, and a *back-stress* builds. To deform further, the
    applied stress must be raised until either the pile-up forces a slip event in the
    next grain, or a new source is activated.

    The smaller the grains, the more boundaries per unit volume, and the stronger the
    metal. The **Hall–Petch equation** quantifies this:

    $$ \sigma_y = \sigma_0 + \frac{k_y}{\sqrt{d}} $$

    | Symbol | Meaning | Typical units |
    |---|---|---|
    | $\sigma_y$ | Yield stress | MPa |
    | $\sigma_0$ | Friction (Peierls) stress — the resistance to dislocation motion *inside* a grain | MPa |
    | $k_y$ | Strengthening coefficient — how effective the boundaries are | MPa·µm$^{1/2}$ |
    | $d$ | Average grain diameter | µm |

    Plotting $\sigma_y$ versus $1/\sqrt{d}$ gives a straight line of slope $k_y$ and
    intercept $\sigma_0$ — the classic *Hall–Petch plot*.
    """)

    with st.expander("📚 Theory deep-dive: pile-up model, normal vs inverse Hall–Petch"):
        st.markdown(r"""
**Origin of the $1/\sqrt{d}$ law (pile-up model).** Consider $n$ dislocations piled up
against a grain boundary under applied shear $\tau$. The leading dislocation feels an
effective stress $n\tau$. For pile-up over a length $\sim d/2$,
$n \approx \pi(1-\nu)\tau d / (2Gb)$. Slip transmits to the next grain when $n\tau$ reaches
a critical value $\tau^*$, giving $\tau - \tau_0 \propto 1/\sqrt{d}$, hence the
square-root law.

**Typical Hall–Petch parameters at room temperature.**

| Material | $\sigma_0$ (MPa) | $k_y$ (MPa·µm$^{1/2}$) |
|---|---|---|
| Copper (FCC) | 25 | 110 |
| Nickel (FCC) | 20 | 158 |
| Aluminium (FCC) | 15 | 70 |
| α-Iron / mild steel (BCC) | 70 | 550 |
| Cobalt (HCP) | 80 | 350 |

BCC metals have larger $k_y$ than FCC because their slip systems are less symmetric and
the back-stress from pile-up is harder to relieve.

**Inverse Hall–Petch — the breakdown at $d \lesssim 10$ nm.**
Below a critical grain size of order **10–20 nm**, the *yield stress decreases* with
further grain refinement. Why? Once the grain is too small to host a Frank–Read
source or a stable pile-up, the deformation mechanism switches from intra-grain
dislocation glide to **grain-boundary sliding** and **diffusional flow** (Coble creep).
The grain boundaries are no longer obstacles — they *are* the deformation pathway.

**Practical consequence.** The peak strength of pure metals occurs around $d \sim$ 10–20 nm.
Going below that softens the material. This is one reason "amorphous metals" (metallic
glasses) — effectively zero grain size — are *not* infinitely strong.
""")

    # Real Hall–Petch plot with REALISTIC grain sizes (in µm)
    # Format:  (d_µm, σ_y MPa)  -- coarse, micro, nano
    hp_database_for_plot = {
        "Nickel (FCC)":   [(100.0, 100), (1.0, 250), (0.020, 1100)],
        "Copper (FCC)":   [(50.0,  40),  (1.0, 140), (0.030, 750)],
        "Cobalt (HCP)":   [(50.0,  150), (1.0, 350), (0.040, 1050)],
        "Tungsten (BCC)": [(50.0,  1000),(1.0, 1800),(0.050, 2400)],
        "316L Steel":     [(50.0,  220), (1.0, 450), (0.040, 1400)],
    }
    fig_hp, ax_hp = plt.subplots(figsize=(8.5, 4.4))
    cmap = plt.cm.tab10
    for i, (name, pts) in enumerate(hp_database_for_plot.items()):
        d_um = np.array([p[0] for p in pts])
        sy   = np.array([p[1] for p in pts])
        invsqrtd = 1.0 / np.sqrt(d_um)
        m, b = np.polyfit(invsqrtd, sy, 1)
        x_line = np.linspace(0, invsqrtd.max()*1.05, 50)
        ax_hp.plot(x_line, m*x_line + b, "-", lw=1.5, color=cmap(i), alpha=0.75)
        ax_hp.plot(invsqrtd, sy, "o", color=cmap(i), markersize=8,
                   label=f"{name}  (k≈{m:.0f}, σ₀≈{max(0,b):.0f})", mec='white', mew=0.8)
    ax_hp.set_xlabel(r"$1/\sqrt{d}$  (µm$^{-1/2}$)")
    ax_hp.set_ylabel(r"Yield stress $\sigma_y$ (MPa)")
    ax_hp.set_title(r"Hall–Petch plot: $\sigma_y = \sigma_0 + k_y/\sqrt{d}$ for the materials in this lab")
    ax_hp.grid(True, alpha=0.3)
    ax_hp.legend(loc='upper left', fontsize=9, framealpha=0.85,
                 title=r"$k_y$ in MPa·µm$^{1/2}$, $\sigma_0$ in MPa")
    ax_hp.set_xlim(left=0)
    ax_hp.set_ylim(bottom=0)
    fig_hp.tight_layout()
    st.pyplot(fig_hp, width="stretch")
    plt.close(fig_hp)

    st.caption("""
    Each point is one of the three grain sizes (coarse / micro / nano) used by the
    simulator below. The straight-line fits confirm the $1/\\sqrt{d}$ law over four
    orders of magnitude in $d$. The slope is $k_y$, the y-intercept is $\\sigma_0$.
    Tungsten sits high because of its enormous Peierls stress; copper sits low because
    its FCC lattice glides very easily in single crystals.
    """)

    with st.expander("🕹️ How to play with this simulator — guided exercises"):
        st.markdown("""
**Setup.** Pick a *base material* on the left (Ni, Cu, Co, W, 316L, or Al₂O₃),
then choose *coarse / micro / nano* grain size. Press **🚀 Start Tensile Test**.

**The dashboard reports** Strain, Stress, Tangent E (the constant initial modulus),
Secant E (live ratio σ/ε), and the Grain Size category.

**The right canvas overlays three curves**: the active grain size in **red** plus the
other two grain sizes faded in white as references. So a single test gives you the
direct comparison "what would have happened with a different grain size."

**Exercise 1 — verify the Hall–Petch law for nickel.**
1. Run Ni *coarse* — record YS.  2. Run Ni *micro* — record YS.  3. Run Ni *nano* — record YS.
Plot $\\sigma_y$ vs $1/\\sqrt{d}$ on paper using $d$ = 100, 1, 0.02 µm.
You should get a straight line with $k_y \\approx$ 150 MPa·µm$^{1/2}$.

**Exercise 2 — see ductility collapse with grain refinement.**
For Cu, the coarse sample stretches to ε = 0.45 (45 %) before fracture, the nano
sample to only 0.02 (2 %). Strength is gained but ductility is lost — the classic
**strength-ductility trade-off**. Note the disappearance of the necking heat-stripe
in the nano case.

**Exercise 3 — compare BCC vs FCC.**
Run Tungsten (BCC) coarse and Copper (FCC) coarse side-by-side. W yields above 1000 MPa,
Cu below 50 MPa. The Hall–Petch plot shows W has a steeper slope: BCC's kink-pair
mechanism makes its boundaries even more effective obstacles.

**Exercise 4 — ceramic Hall–Petch.**
Run Al₂O₃ *coarse* (linear elastic to ~0.04 % strain), then Al₂O₃ *nano*.
The strength quadruples (150 → 600 MPa) — Hall–Petch works in ceramics too,
even though no dislocations are involved. There the mechanism is **Griffith flaw size
limited by grain size**, not pile-up.

**Exercise 5 — the strain-hardening exponent.**
The reference curves on the right reveal that nano-grained metals have a
much *flatter* plastic plateau than coarse ones. The exponent $n$ in
$\\sigma = K\\varepsilon^n$ drops from $\\sim 0.20$ (coarse Ni) to $\\sim 0.05$ (nano Ni).
Less room to work-harden = earlier necking.
""")

    with st.expander("📐 Worked exercises with formulas — solve these by hand"):
        st.markdown(r"""
Hall–Petch is one of the cleanest equations in materials science — and it lets you make
quantitative engineering predictions in a single line of algebra.

---

### Exercise 1 — Predict $\sigma_y$ at a given grain size
Pure copper: $\sigma_0 = 25$ MPa, $k_y = 110\;\text{MPa}\cdot\mu\text{m}^{1/2}$. What is the yield stress at $d = 10\,\mu\text{m}$?

**Formula.** $\sigma_y = \sigma_0 + k_y/\sqrt{d}$

**Solution.** $\sigma_y = 25 + 110/\sqrt{10} = 25 + 34.78 = \mathbf{59.8\;\text{MPa}}$

---

### Exercise 2 — Inverse problem: target a yield strength
Same copper. You need a yield strength of 200 MPa. What grain size do you need?

**Solve for $d$.**
$$d = \left(\frac{k_y}{\sigma_y - \sigma_0}\right)^{2}$$

**Solution.**
- $\sqrt{d} = 110/(200-25) = 110/175 = 0.629\;\mu\text{m}^{1/2}$
- $d = 0.629^2 = \mathbf{0.395\;\mu\text{m} = 395\;\text{nm}}$

> So you need ultrafine grains. This is the entire premise of Severe Plastic Deformation
> (SPD) processes like ECAP and HPT — engineer the microstructure, dial in the strength.

---

### Exercise 3 — Extract Hall–Petch constants from two data points
Two nickel samples are tested:
- $d_1 = 100\,\mu\text{m}$ → $\sigma_{y,1} = 110$ MPa
- $d_2 = 1\,\mu\text{m}$ → $\sigma_{y,2} = 250$ MPa

**Strategy.** Plot $\sigma_y$ vs $1/\sqrt{d}$ — the slope is $k_y$ and the intercept is $\sigma_0$.

- $1/\sqrt{d_1} = 1/\sqrt{100} = 0.10$
- $1/\sqrt{d_2} = 1/\sqrt{1} = 1.00$
- $k_y = (\sigma_{y,2}-\sigma_{y,1})/(1/\sqrt{d_2} - 1/\sqrt{d_1}) = (250-110)/(1.00-0.10) = 140/0.90 = \mathbf{155.6\;\text{MPa}\cdot\mu\text{m}^{1/2}}$
- $\sigma_0 = 110 - 155.6\times 0.10 = \mathbf{94.4\;\text{MPa}}$

> Compare with the literature: Ni has $k_y$ in the range 100–200 MPa·µm$^{1/2}$, $\sigma_0 \approx 50$–100 MPa.
> Our two-point fit lands squarely in the textbook window — but **always use $\geq 4$ points** in real work
> to test whether the linear $1/\sqrt{d}$ scaling actually holds.

---

### Exercise 4 — Where does Hall–Petch break? (Inverse Hall–Petch)
Use the Cu fit from Ex 1 to **extrapolate** to $d = 5\,\text{nm} = 0.005\,\mu\text{m}$.

**Solution.** $\sigma_y = 25 + 110/\sqrt{0.005} = 25 + 1556 = \mathbf{\sim 1580\;\text{MPa}}$ (predicted)

**Real measurements:** Cu nanograins at $d = 5$ nm yield around $700$ MPa — less than half
the H–P prediction.

> **Why?** Below $d \approx 10$ nm the deformation mode flips from dislocation glide to
> grain-boundary sliding and rotation. Hall–Petch — built on the pile-up model — has no
> right to apply. **Don't extrapolate H–P below ~ 20 nm.**

---

### Exercise 5 — Resilience scales with grain refinement
For copper ($E = 130$ GPa) compute the modulus of resilience at two grain sizes:

**Formula.** $U_r = \sigma_y^{\,2}/(2E)$

| Grain size $d$ | $\sigma_y$ (from Ex 1 formula) | $U_r$ |
|---|---|---|
| $100\,\mu\text{m}$ | $25 + 110/10 = 36$ MPa | $36^2/(2\times 130000) = \mathbf{4.99\;\text{kJ/m}^3}$ |
| $1\,\mu\text{m}$ | $25 + 110 = 135$ MPa | $135^2/(2\times 130000) = \mathbf{70.1\;\text{kJ/m}^3}$ |

> **Refining the grains by a factor of 100 multiplies $U_r$ by ~14×** — useful for spring
> applications where you want to store maximum elastic energy without yielding.

---

### Exercise 6 — Combine grain refinement + work hardening
A 316L stainless sheet with $d = 10\,\mu\text{m}$ ($\sigma_0 = 196$, $k_y = 241$ MPa·µm$^{1/2}$) is
cold rolled, raising $\rho$ from $10^{12}$ to $10^{14}\;\text{m}^{-2}$. Use Taylor with $\alpha=0.3$,
$G=78$ GPa, $b=0.255$ nm to add the dislocation contribution.

**Step 1 — H–P contribution.** $\sigma_{HP} = 196 + 241/\sqrt{10} = 196 + 76.2 = 272.2$ MPa.

**Step 2 — Taylor before/after.**
- $\tau = \alpha G b\sqrt{\rho}$
- Before: $\tau = 0.3 \times 78\times 10^9 \times 0.255\times 10^{-9}\times \sqrt{10^{12}} = 5.97$ MPa
- After: $\tau = 0.3 \times 78\times 10^9 \times 0.255\times 10^{-9}\times \sqrt{10^{14}} = 59.7$ MPa
- $\Delta\tau = 53.7$ MPa, $\Delta\sigma \approx 2\Delta\tau = 107$ MPa (Taylor factor $\approx 2$ for FCC poly)

**Step 3 — Combined** (additive): $\sigma_{y,\text{cold}} \approx 272 + 107 \approx \mathbf{380\;\text{MPa}}$.

> Matches the typical YS of half-hard 316L ($\approx 380$–420 MPa) — quantitative validation
> that the four strengthening mechanisms really do add (approximately).
""")

    # ---- Hidden bonus exercise (gated) ----
    hidden_exercise(
        key_prefix="t4_bonus",
        title="🔒 Hidden bonus exercise — only opens if you remember the inverse Hall–Petch crossover",
        gate_question=(
            "Below approximately what grain size (in **nanometers**, integer) does the *inverse* "
            "Hall–Petch effect typically begin to dominate?"
        ),
        hint="The number is mentioned in BOTH the deep-dive AND Worked Exercise 4 of this tab.",
        accepted_answers=["10", "15", "20", "12"],
        numeric_target=15,
        numeric_tolerance=8,  # accepts 7–23 nm — all defensible literature values
        exercise_md=r"""
### 🏆 Bonus — The absurd extrapolation: where Hall–Petch hits the ideal-strength ceiling

Use the copper Hall–Petch fit from *Worked Exercise 1* ($\sigma_0 = 25$ MPa, $k_y = 110$ MPa·µm$^{1/2}$).
Pure copper has $E = 130$ GPa; the **theoretical (ideal) strength** of any crystal is approximately
$\sigma_{\text{ideal}} \approx E/10 = 13$ GPa $= 13\,000$ MPa.

**Problem.** At what grain size $d^{*}$ would the Hall–Petch formula predict that the yield
strength reaches the ideal strength of copper? Comment on the result.

---

**Solution.**
$$13\,000 = 25 + \frac{110}{\sqrt{d^{*}}} \;\Rightarrow\; \sqrt{d^{*}} = \frac{110}{12\,975} = 8.48\times 10^{-3}\;\mu\text{m}^{1/2}$$
$$d^{*} = (8.48\times 10^{-3})^{2} = 7.2\times 10^{-5}\;\mu\text{m} = 7.2\times 10^{-2}\;\text{nm} = \mathbf{0.072\;\text{nm} = 72\;\text{pm}}$$

> **Reflection.** A copper atom has a diameter of about **256 pm**. The Hall–Petch equation
> would require us to make grains *smaller than a single atom* to reach the ideal strength —
> a manifest absurdity. The mechanism MUST break down long before this. The fact that experiments
> show the breakdown at $d \sim 10$–20 nm (where there are still ~50 atoms across each grain)
> is consistent with grain-boundary sliding taking over once the grain is too small to support
> a coherent dislocation pile-up. **Always sanity-check an extrapolation against a physical limit.**
""",
    )

    st.divider()

    hp_database = {
        "Nickel (FCC)":           {"color":"#A9A9A9","type":"metal","poisson":0.31,"n":0.20,
            "coarse":{"name":"Coarse (~100 µm)","E":200000,"YS":100,"UTS":350,"max_strain":0.50,"gs":150,"soft":0.30},
            "micro": {"name":"Micro (~1 µm)","E":200000,"YS":250,"UTS":500,"max_strain":0.25,"gs":40,"soft":0.25},
            "nano":  {"name":"Nano (~20 nm)","E":200000,"YS":1100,"UTS":1200,"max_strain":0.03,"gs":8,"soft":0.10}},
        "Copper (FCC)":           {"color":"#B87333","type":"metal","poisson":0.34,"n":0.18,
            "coarse":{"name":"Coarse (~50 µm)","E":110000,"YS":40,"UTS":220,"max_strain":0.45,"gs":150,"soft":0.30},
            "micro": {"name":"Micro (~1 µm)","E":110000,"YS":140,"UTS":300,"max_strain":0.20,"gs":40,"soft":0.20},
            "nano":  {"name":"Nano (~30 nm)","E":110000,"YS":750,"UTS":800,"max_strain":0.02,"gs":8,"soft":0.10}},
        "Cobalt (HCP)":           {"color":"#4682B4","type":"metal","poisson":0.31,"n":0.12,
            "coarse":{"name":"Coarse (~50 µm)","E":209000,"YS":150,"UTS":400,"max_strain":0.25,"gs":150,"soft":0.20},
            "micro": {"name":"Micro (~1 µm)","E":209000,"YS":350,"UTS":600,"max_strain":0.12,"gs":40,"soft":0.15},
            "nano":  {"name":"Nano (~40 nm)","E":209000,"YS":1050,"UTS":1200,"max_strain":0.015,"gs":8,"soft":0.08}},
        "Tungsten (BCC)":         {"color":"#708090","type":"metal","poisson":0.28,"n":0.10,
            "coarse":{"name":"Coarse (~50 µm)","E":411000,"YS":1000,"UTS":1100,"max_strain":0.05,"gs":150,"soft":0.10},
            "micro": {"name":"Micro (~1 µm)","E":411000,"YS":1800,"UTS":1900,"max_strain":0.02,"gs":40,"soft":0.08},
            "nano":  {"name":"Nano (~50 nm)","E":411000,"YS":2400,"UTS":2600,"max_strain":0.012,"gs":8,"soft":0.05}},
        "Stainless Steel (316L)": {"color":"#87CEFA","type":"metal","poisson":0.30,"n":0.30,
            "coarse":{"name":"Coarse (~50 µm)","E":193000,"YS":220,"UTS":550,"max_strain":0.55,"gs":150,"soft":0.30},
            "micro": {"name":"Micro (~1 µm)","E":193000,"YS":450,"UTS":750,"max_strain":0.30,"gs":40,"soft":0.25},
            "nano":  {"name":"Nano (~40 nm)","E":193000,"YS":1400,"UTS":1600,"max_strain":0.04,"gs":8,"soft":0.10}},
        "Alumina (Al2O3 Ceramic)":{"color":"#F5F5DC","type":"ceramic","poisson":0.22,
            "coarse":{"name":"Coarse (~50 µm)","E":370000,"YS":150,"UTS":150,"max_strain":0.0004,"gs":150},
            "micro": {"name":"Micro (~1 µm)","E":370000,"YS":300,"UTS":300,"max_strain":0.0008,"gs":40},
            "nano":  {"name":"Nano (~50 nm)","E":370000,"YS":600,"UTS":600,"max_strain":0.0016,"gs":8}},
    }

    col_ui2, col_sim2 = st.columns([1, 5])
    with col_ui2:
        st.subheader("Experiment Setup")
        sel_mat_hp = st.selectbox("Base Material", list(hp_database.keys()), key="t2_mat")
        sel_grain = st.radio("Grain Size", ["coarse","micro","nano"], format_func=lambda x: hp_database[sel_mat_hp][x]["name"], key="t2_grain")
        speed_hp = st.slider("Testing Speed", 0.5, 3.0, 1.0, 0.5, key="t2_speed")
        matFam = hp_database[sel_mat_hp]; actM = matFam[sel_grain]
        st.divider()
        st.markdown(f"**E (Initial):** {actM['E']:,} MPa  \n**YS:** {actM['YS'] if matFam['type']=='metal' else 'Brittle'} MPa  \n**UTS:** {actM['UTS']:,} MPa  \n**Max Strain:** {actM['max_strain']*100:.2f}%")
        st.info(r"💡 Secant modulus $\sigma/\varepsilon$ drops sharply once plasticity starts — compare against the constant tangent E above.")

    html_code_2 = f"""
    <!DOCTYPE html><html><head><style>
        body {{ font-family: sans-serif; color: white; background: #0e1117; margin: 0; padding: 10px; }}
        .dashboard {{ display: flex; justify-content: space-between; margin-bottom: 10px; background: #262730; padding: 15px; border-radius: 8px; }}
        .metric {{ text-align: center; }} .value {{ font-size: 20px; font-weight: bold; color: #4CAF50; }} .label {{ font-size: 11px; color: #aaa; text-transform: uppercase; }}
        .container {{ display: flex; gap: 15px; height: 600px; }}
        .canvas-wrapper {{ background: #1e1e1e; border-radius: 8px; position: relative; overflow: hidden; border: 1px solid #444; }}
        #sW, #mW {{ flex: 1; }} #gW {{ flex: 1.5; }}
        canvas {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: block; }}
        .panel-title {{ position: absolute; top: 10px; left: 10px; z-index: 10; font-size: 12px; color: #ddd; font-weight: bold; background: rgba(0,0,0,0.7); padding: 5px; border-radius: 4px; }}
        .btn {{ background: #FF4B4B; color: white; border: none; padding: 10px; border-radius: 4px; cursor: pointer; font-weight: bold; width: 100%; margin-bottom: 10px; text-transform: uppercase; }}
    </style></head><body>
        <button id="startBtn2" class="btn">🚀 Start Tensile Test</button>
        <div class="dashboard">
            <div class="metric"><div class="label">Strain (\u03B5)</div><div class="value" id="val_strain2">0.0000</div></div>
            <div class="metric"><div class="label">Stress (\u03C3)</div><div class="value" id="val_stress2">0.0 MPa</div></div>
            <div class="metric"><div class="label">Tangent E (init)</div><div class="value" style="color:#FFD700;">{actM['E']:,} MPa</div></div>
            <div class="metric"><div class="label">Secant E (live)</div><div class="value" id="val_mod2" style="color:#FFA500;">{actM['E']:,} MPa</div></div>
            <div class="metric"><div class="label">Grain Size</div><div class="value" style="color:#FFA500;">{sel_grain.upper()}</div></div>
        </div>
        <div class="container">
            <div class="canvas-wrapper" id="sW"><div class="panel-title">Macro</div><canvas id="sC"></canvas></div>
            <div class="canvas-wrapper" id="mW"><div class="panel-title">Micro Boundary Logic</div><canvas id="mC"></canvas></div>
            <div class="canvas-wrapper" id="gW"><div class="panel-title">Hall-Petch Comparison</div><canvas id="gC"></canvas></div>
        </div>
        <script>
            const fam = {json.dumps(matFam)}; const actK = "{sel_grain}"; const am = fam[actK]; const spd = {speed_hp};
            let run = false; let strn = 0; let hData = []; let disl = [];
            const L0 = 50.0; const W0 = 12.5; const T0 = 2.0;

            function widthAtStrain(eps) {{
                if(eps <= 0) return W0;
                return W0 * Math.pow(1 + eps, -fam.poisson);
            }}

            function initPhy() {{
                disl = [];
                if(fam.type === "metal") {{
                    const n = (actK==="nano") ? 80 : (actK==="micro" ? 40 : 15);
                    for(let i=0;i<n;i++) disl.push({{ x:Math.random()*400, y:Math.random()*400, a:(Math.random()>0.5?45:-45)*Math.PI/180, act:false, s:1+Math.random(), st:(am.YS/am.E)+Math.random()*am.max_strain*0.1 }});
                }}
            }}

            function cS(e, p) {{
                if(fam.type === "ceramic") return e >= p.max_strain ? 0 : e * p.E;
                const eY = p.YS / p.E;
                if(e <= eY) return e * p.E;
                const platEnd = eY;
                const eUts = Math.max(platEnd + 1e-4, p.max_strain * 0.6);
                if(e <= eUts) {{
                    const n = fam.n || 0.2;
                    const r = (e - platEnd) / (eUts - platEnd);
                    return Math.min(p.UTS, p.YS + (p.UTS - p.YS) * Math.pow(Math.max(0,r), n));
                }}
                const soft = (p.soft === undefined) ? 0.20 : p.soft;
                const t = (e - eUts) / (p.max_strain - eUts);
                return Math.max(0, p.UTS * (1 - soft * t * t));
            }}

            function dGraph() {{
                const c = document.getElementById('gC'); const ctx = c.getContext('2d');
                c.width = c.parentElement.clientWidth; c.height = c.parentElement.clientHeight;
                ctx.clearRect(0,0,c.width,c.height);
                const px=70, py=50, pr=80, pt=40;
                const w = c.width-px-pr; const h = c.height-py-pt;
                const mE = Math.max(fam.coarse.max_strain, fam.micro.max_strain, fam.nano.max_strain) * 1.15;
                const mS = Math.max(fam.coarse.UTS, fam.micro.UTS, fam.nano.UTS) * 1.30;
                const gX = (v) => px + (v/mE)*w; const gY = (v) => c.height - py - (v/mS)*h;

                ctx.strokeStyle='#888'; ctx.lineWidth=2; ctx.beginPath();
                ctx.moveTo(px,pt); ctx.lineTo(px,c.height-py); ctx.lineTo(c.width-pr,c.height-py); ctx.stroke();
                ctx.fillStyle='#aaa'; ctx.font='11px sans-serif'; ctx.textAlign='right';
                for(let i=0;i<=5;i++) {{ const v=(mS/5)*i; const y=gY(v); ctx.fillText(Math.round(v),px-10,y+4); ctx.strokeStyle='#333'; ctx.beginPath(); ctx.moveTo(px,y); ctx.lineTo(c.width-pr,y); ctx.stroke(); }}
                ctx.save(); ctx.translate(20,c.height/2); ctx.rotate(-Math.PI/2); ctx.textAlign='center'; ctx.fillText('Stress (MPa)',0,0); ctx.restore();

                ctx.textAlign='center';
                for(let i=0;i<=5;i++) {{ const v=(mE/5)*i; const x=gX(v); ctx.fillText(v.toFixed(3),x,c.height-py+20); ctx.strokeStyle='#333'; ctx.beginPath(); ctx.moveTo(x,c.height-py); ctx.lineTo(x,pt); ctx.stroke(); }}
                ctx.fillText('Strain (\u03B5)',px+w/2,c.height-10);

                ['coarse','micro','nano'].forEach(k => {{
                    const p = fam[k];
                    ctx.strokeStyle = k === actK ? 'rgba(0,0,0,0)' : 'rgba(255,255,255,0.25)';
                    ctx.lineWidth=2; ctx.setLineDash([5,5]);
                    ctx.beginPath(); ctx.moveTo(gX(0), gY(0));
                    for(let e=0; e<=p.max_strain; e+=p.max_strain/120) ctx.lineTo(gX(e), gY(cS(e,p)));
                    ctx.stroke(); ctx.setLineDash([]);
                    if(k !== actK) {{ ctx.fillStyle='rgba(255,255,255,0.5)'; ctx.fillText(p.name.split(" ")[0], gX(p.max_strain)+20, gY(cS(p.max_strain,p))); }}
                }});

                if(hData.length > 0) {{
                    ctx.strokeStyle='#FF4B4B'; ctx.lineWidth=4; ctx.beginPath();
                    ctx.moveTo(gX(hData[0].x), gY(hData[0].y));
                    for(let i=1;i<hData.length;i++) ctx.lineTo(gX(hData[i].x), gY(hData[i].y));
                    ctx.stroke();
                    ctx.fillStyle='#fff'; ctx.beginPath();
                    ctx.arc(gX(hData[hData.length-1].x), gY(hData[hData.length-1].y), 5, 0, Math.PI*2); ctx.fill();
                }}
            }}

            function dMac() {{
                const c = document.getElementById('sC'); const ctx = c.getContext('2d');
                c.width = c.parentElement.clientWidth; c.height = c.parentElement.clientHeight;
                ctx.clearRect(0,0,c.width,c.height);
                const frac = strn >= am.max_strain;
                const dE = frac ? am.max_strain : strn;
                const W = widthAtStrain(dE);
                const L = L0 * (1 + dE);
                const neckOnset = am.max_strain*0.6;
                const neck = (dE > neckOnset && fam.type !== "ceramic") ? W*0.4*((dE - neckOnset)/(am.max_strain - neckOnset)) : 0;
                const sc = c.height/(L0*1.8 + 80);
                const cx = c.width/2, cy = c.height/2;

                let minW = W;
                ctx.beginPath();
                for(let y=-L/2; y<=L/2; y+=L/60) {{
                    let cW = (W/2) - (neck * Math.exp(-(y*y)/(L0*0.2)));
                    if(Math.abs(y) > L/2 - L0*0.1) cW = W0*0.9;
                    let py = cy + y*sc; if(frac && y>0) py += 10;
                    if(y === -L/2) ctx.moveTo(cx + cW*sc, py); else ctx.lineTo(cx + cW*sc, py);
                    if(cW*2 < minW) minW = cW*2;
                }}
                for(let y=L/2; y>=-L/2; y-=L/60) {{
                    let cW = (W/2) - (neck * Math.exp(-(y*y)/(L0*0.2)));
                    if(Math.abs(y) > L/2 - L0*0.1) cW = W0*0.9;
                    let py = cy + y*sc; if(frac && y>0) py += 10;
                    ctx.lineTo(cx - cW*sc, py);
                }}
                ctx.closePath(); ctx.fillStyle = fam.color; ctx.fill();

                ctx.save(); ctx.clip();
                const ye = am.YS ? am.YS/am.E : 0;
                if(dE > ye && fam.type !== "ceramic") {{
                    const pp = Math.min(1, (dE - ye)/(am.max_strain - ye));
                    const heatHalfH = (neck > 0) ? (L0*0.15)*sc : (L*0.25)*sc;
                    const grd = ctx.createLinearGradient(0, cy - heatHalfH, 0, cy + heatHalfH);
                    grd.addColorStop(0, "transparent"); grd.addColorStop(0.5, `rgba(255, 69, 0, ${{pp*0.6}})`); grd.addColorStop(1, "transparent");
                    ctx.fillStyle = grd; ctx.fillRect(cx - W0*sc, cy - heatHalfH, W0*2*sc, 2*heatHalfH);
                }}
                ctx.restore(); ctx.strokeStyle="white"; ctx.lineWidth=1; ctx.stroke();

                ctx.fillStyle='#2F4F4F';
                const gW = W0*2.2*sc, gH = 40;
                ctx.fillRect(cx - gW/2, cy - (L/2)*sc - gH + 5, gW, gH);
                ctx.fillRect(cx - gW/2, cy + (L/2)*sc + (frac?10:0) - 5, gW, gH);

                const cStrss = cS(dE, am);
                const cMod = (strn > 1e-4 && !frac) ? (cStrss / strn).toFixed(0) : (frac ? "0" : am.E);
                document.getElementById('val_strain2').innerText = strn.toFixed(4);
                document.getElementById('val_stress2').innerText = frac ? "Fractured" : (cStrss.toFixed(1) + " MPa");
                document.getElementById('val_mod2').innerText  = cMod + " MPa";
            }}

            function dMic() {{
                const c = document.getElementById('mC'); const ctx = c.getContext('2d');
                c.width = c.parentElement.clientWidth; c.height = c.parentElement.clientHeight;
                const frac = strn >= am.max_strain;
                ctx.fillStyle='#111'; ctx.fillRect(0,0,c.width,c.height);

                if(fam.type === "metal") {{
                    const gs = am.gs;
                    ctx.strokeStyle='#444'; ctx.lineWidth=1.5;
                    ctx.beginPath();
                    for(let x=-gs; x<c.width+gs; x+=gs) for(let y=-gs; y<c.height+gs; y+=gs) {{
                        const off = (Math.floor(y/gs)%2===0) ? 0 : gs/2;
                        ctx.rect(x-off, y, gs, gs);
                    }}
                    ctx.stroke();
                    ctx.strokeStyle='#FFeb3b'; ctx.lineWidth=2;
                    disl.forEach(d => {{
                        if(strn > d.st && !frac) d.act = true;
                        if(d.act) {{
                            d.x += Math.cos(d.a)*d.s; d.y += Math.sin(d.a)*d.s;
                            const lx = ((d.x % gs) + gs) % gs, ly = ((d.y % gs) + gs) % gs;
                            if(lx < 3 || ly < 3 || lx > gs-3 || ly > gs-3) d.s *= 0.92;
                        }}
                        ctx.save();
                        ctx.translate(((d.x % c.width)+c.width)%c.width, ((d.y % c.height)+c.height)%c.height);
                        ctx.rotate(d.a);
                        ctx.beginPath(); ctx.moveTo(-6,0); ctx.lineTo(6,0); ctx.moveTo(0,0); ctx.lineTo(0,10); ctx.stroke();
                        ctx.restore();
                    }});
                }} else if(fam.type === "ceramic") {{
                    const gs = am.gs;
                    ctx.fillStyle='#aaa';
                    for(let x=gs/2; x<c.width; x+=gs) for(let y=gs/2; y<c.height; y+=gs) {{
                        ctx.beginPath(); ctx.arc(x, y, gs/3, 0, Math.PI*2); ctx.fill();
                    }}
                    const r = strn/am.max_strain;
                    if(r > 0.8) {{
                        ctx.strokeStyle = `rgba(255,75,75,${{(r-0.8)*5}})`; ctx.lineWidth = 1.5;
                        for(let i=0; i<6; i++) {{
                            const sx = c.width*0.3 + i*15, sy = c.height*0.5 + Math.sin(i)*20;
                            ctx.beginPath(); ctx.moveTo(sx, sy); ctx.lineTo(sx + Math.cos(i)*10, sy + Math.sin(i)*10); ctx.stroke();
                        }}
                    }}
                }}
                if(frac) {{ ctx.strokeStyle='#FF4B4B'; ctx.lineWidth=6; ctx.beginPath(); ctx.moveTo(c.width/2,0); ctx.lineTo(c.width/2-15,c.height*0.4); ctx.lineTo(c.width/2+20,c.height*0.7); ctx.lineTo(c.width/2,c.height); ctx.stroke(); ctx.fillStyle="rgba(0,0,0,0.6)"; ctx.fillRect(0,0,c.width,c.height); }}
            }}

            function loop2() {{
                if(!run) return;
                let inc = (am.max_strain/400) * spd;
                if(fam.type !== "ceramic" && strn < (am.YS/am.E)) inc *= 0.4;
                strn += inc;
                if(strn >= am.max_strain) {{
                    strn = am.max_strain;
                    hData.push({{x:strn, y:cS(strn,am)}});
                    dMac(); dMic(); dGraph();
                    document.getElementById('startBtn2').innerText = "TEST COMPLETE - RESET";
                    run = false; return;
                }}
                hData.push({{x:strn, y:cS(strn,am)}});
                dMac(); dMic(); dGraph();
                requestAnimationFrame(loop2);
            }}

            document.getElementById('startBtn2').addEventListener('click', () => {{
                const btn = document.getElementById('startBtn2');
                if(btn.innerText.includes("RESET")) {{
                    strn=0; hData=[]; initPhy(); dMac(); dMic(); dGraph();
                    btn.innerText = "🚀 Start Tensile Test"; return;
                }}
                run=true; loop2();
            }});

            initPhy(); dMac(); dMic(); dGraph();
            window.addEventListener('resize', () => {{ if(!run) {{ dMac(); dMic(); dGraph(); }} }});
        </script>
    </body></html>
    """
    with col_sim2:
        components.html(html_code_2, height=750, scrolling=False)

# ===================================================================
# TAB 5: ATOMIC ORIGIN OF YOUNG'S MODULUS — Lennard-Jones vs Morse
# ===================================================================
with tab5:
    st.markdown("### ⚛️ From Interatomic Potential to Young's Modulus")
    st.caption("Young's modulus emerges from the curvature of U(r) at the equilibrium bond length. Compare the Lennard-Jones (12-6) and Morse approximations side-by-side.")
    st.latex(r"E \;\approx\; \frac{1}{r_0}\left.\frac{\partial^2 U}{\partial r^2}\right|_{r_0} \quad\text{with}\quad k_{\text{bond}} = \left.\frac{\partial^2 U}{\partial r^2}\right|_{r_0}")

    # Morse parameters from Girifalco & Weizer (1959); LJ parameters from standard references.
    atomic_db = {
        "Copper (Cu)":   {"morse": {"D": 0.3429, "a": 1.3588, "r0": 2.866}, "lj": {"eps": 0.4093, "sigma": 2.338}, "E_exp": 110, "lattice": "FCC", "color": "#B87333"},
        "Iron (Fe)":     {"morse": {"D": 0.4174, "a": 1.3885, "r0": 2.845}, "lj": {"eps": 0.521,  "sigma": 2.321}, "E_exp": 211, "lattice": "BCC", "color": "#A0A8B0"},
        "Aluminum (Al)": {"morse": {"D": 0.2703, "a": 1.1646, "r0": 3.253}, "lj": {"eps": 0.337,  "sigma": 2.620}, "E_exp": 70,  "lattice": "FCC", "color": "#D8D8E0"},
        "Silver (Ag)":   {"morse": {"D": 0.3323, "a": 1.3690, "r0": 3.115}, "lj": {"eps": 0.345,  "sigma": 2.594}, "E_exp": 83,  "lattice": "FCC", "color": "#E8E8E8"},
        "Nickel (Ni)":   {"morse": {"D": 0.4205, "a": 1.4199, "r0": 2.780}, "lj": {"eps": 0.520,  "sigma": 2.282}, "E_exp": 200, "lattice": "FCC", "color": "#A8B0B8"},
        "Tungsten (W)":  {"morse": {"D": 0.9906, "a": 1.4116, "r0": 2.740}, "lj": {"eps": 1.060,  "sigma": 2.295}, "E_exp": 411, "lattice": "BCC", "color": "#708090"},
        "Argon (Ar)":    {"morse": {"D": 0.0104, "a": 1.490,  "r0": 3.760}, "lj": {"eps": 0.0104, "sigma": 3.405}, "E_exp": 0,   "lattice": "FCC", "color": "#88AAFF"},
    }

    col_ui3, col_sim3 = st.columns([1, 5])
    with col_ui3:
        st.subheader("Atomic Parameters")
        sel_atom = st.selectbox("Element", list(atomic_db.keys()), key="t3_mat")
        ad = atomic_db[sel_atom]

        potential = st.radio("Active potential", ["Morse", "Lennard-Jones (12-6)"], key="t3_pot",
                             help="The selected potential is drawn bold; the other is faded for comparison.")

        st.divider()
        if potential == "Morse":
            st.markdown("**Morse**")
            st.caption("U(r) = D·[(1−e^(−α(r−r₀)))² − 1]")
            D     = st.slider("D — well depth (eV)",     0.005, 1.5, float(ad["morse"]["D"]),  0.005, key="t3_D")
            a     = st.slider("α — width (1/Å)",         0.5,   2.5, float(ad["morse"]["a"]),  0.05,  key="t3_a")
            r0_in = st.slider("r₀ — equilibrium (Å)",    1.5,   4.5, float(ad["morse"]["r0"]), 0.05,  key="t3_r0")
            eps   = ad["lj"]["eps"]; sigma = ad["lj"]["sigma"]
        else:
            st.markdown("**Lennard-Jones**")
            st.caption("U(r) = 4ε·[(σ/r)¹² − (σ/r)⁶]")
            eps   = st.slider("ε — well depth (eV)",     0.005, 1.5, float(ad["lj"]["eps"]),   0.005, key="t3_eps")
            sigma = st.slider("σ — distance scale (Å)",  1.5,   4.0, float(ad["lj"]["sigma"]), 0.05,  key="t3_sigma")
            D = ad["morse"]["D"]; a = ad["morse"]["a"]; r0_in = ad["morse"]["r0"]

        speed_t3 = st.slider("Animation speed", 0.5, 3.0, 1.0, 0.5, key="t3_speed")
        st.divider()
        E_exp_disp = f"{ad['E_exp']} GPa" if ad['E_exp'] else "— (gas)"
        st.markdown(f"**Lattice:** {ad['lattice']}  \n**E (experimental):** {E_exp_disp}")

    pot_key = "morse" if potential == "Morse" else "lj"
    E_exp_val = ad["E_exp"] if ad["E_exp"] else 0

    html_code_3 = f"""
    <!DOCTYPE html><html><head><style>
        body {{ font-family: sans-serif; color: white; background: #0e1117; margin: 0; padding: 10px; }}
        .dashboard {{ display: flex; justify-content: space-between; margin-bottom: 10px; background: #262730; padding: 12px; border-radius: 8px; gap: 8px; }}
        .metric {{ text-align: center; flex: 1; }}
        .value {{ font-size: 17px; font-weight: bold; color: #4CAF50; }}
        .label {{ font-size: 10px; color: #aaa; text-transform: uppercase; letter-spacing: 0.5px; }}
        .container {{ display: flex; gap: 12px; height: 580px; }}
        .canvas-wrapper {{ background: #1e1e1e; border-radius: 8px; position: relative; overflow: hidden; border: 1px solid #444; flex: 1; }}
        canvas {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: block; }}
        .panel-title {{ position: absolute; top: 10px; left: 10px; z-index: 10; font-size: 12px; color: #ddd; font-weight: bold; background: rgba(0,0,0,0.7); padding: 5px 8px; border-radius: 4px; }}
        .btn {{ background: #FF4B4B; color: white; border: none; padding: 10px; border-radius: 4px; cursor: pointer; font-weight: bold; width: 100%; margin-bottom: 10px; text-transform: uppercase; }}
    </style></head><body>
        <button id="startBtn3" class="btn">▶ Animate Bond Stretch</button>
        <div class="dashboard">
            <div class="metric"><div class="label">r (current)</div><div class="value" id="val_r">—</div></div>
            <div class="metric"><div class="label">U(r)</div><div class="value" id="val_U">—</div></div>
            <div class="metric"><div class="label">F(r)</div><div class="value" id="val_F">—</div></div>
            <div class="metric"><div class="label">k = ∂²U/∂r²|r₀</div><div class="value" style="color:#FFD700;" id="val_k">—</div></div>
            <div class="metric"><div class="label">E (calc, 1D)</div><div class="value" style="color:#FFA500;" id="val_E">—</div></div>
            <div class="metric"><div class="label">E (experiment)</div><div class="value" style="color:#88CCFF;" id="val_Eexp">—</div></div>
        </div>
        <div class="container">
            <div class="canvas-wrapper"><div class="panel-title">U(r) — Energy</div><canvas id="uC"></canvas></div>
            <div class="canvas-wrapper"><div class="panel-title">{ad['lattice']} Lattice</div><canvas id="lC"></canvas></div>
            <div class="canvas-wrapper"><div class="panel-title">F(r) = −∂U/∂r</div><canvas id="fC"></canvas></div>
        </div>
        <script>
            const sel = "{pot_key}";
            const D = {D}; const a = {a}; const r0_morse = {r0_in};
            const eps = {eps}; const sigma = {sigma};
            const lattice = "{ad['lattice']}";
            const matColor = "{ad['color']}";
            const Eexp = {E_exp_val};
            const spd = {speed_t3};

            // --- Equilibrium distances ---
            const r0_lj = sigma * Math.pow(2, 1/6);
            const r0_eq = (sel === "morse") ? r0_morse : r0_lj;

            // --- Potential, force, curvature ---
            function U_morse(r)   {{ const e = Math.exp(-a*(r-r0_morse)); return D*((1-e)*(1-e) - 1); }}
            function dU_morse(r)  {{ const e = Math.exp(-a*(r-r0_morse)); return 2*D*a*e*(1-e); }}
            function d2U_morse(r) {{ const e = Math.exp(-a*(r-r0_morse)); return 2*D*a*a*(2*e*e - e); }}

            function U_lj(r)      {{ const sr = sigma/r; const sr6 = Math.pow(sr,6); return 4*eps*(sr6*sr6 - sr6); }}
            function dU_lj(r)     {{ const sr = sigma/r; const sr6 = Math.pow(sr,6); return 4*eps*(-12*sr6*sr6/r + 6*sr6/r); }}
            function d2U_lj(r)    {{ const sr = sigma/r; const sr6 = Math.pow(sr,6); return 4*eps*(156*sr6*sr6/(r*r) - 42*sr6/(r*r)); }}

            const U_active   = (r) => sel === "morse" ? U_morse(r)   : U_lj(r);
            const dU_active  = (r) => sel === "morse" ? dU_morse(r)  : dU_lj(r);
            const d2U_active = (r) => sel === "morse" ? d2U_morse(r) : d2U_lj(r);

            // --- Derived quantities ---
            const k_eq    = d2U_active(r0_eq);                        // eV/Å²
            const Umin_eq = U_active(r0_eq);
            const E_calc  = (k_eq / r0_eq) * 160.218;                 // GPa  (1 eV/Å³ = 160.218 GPa)
            const U_harm  = (r) => Umin_eq + 0.5*k_eq*(r-r0_eq)*(r-r0_eq);
            const F_harm  = (r) => -k_eq*(r-r0_eq);

            let r_cur = r0_eq;
            let phase = 0;
            let running = false;

            // ============================================================
            //  ENERGY PLOT  U(r)
            // ============================================================
            function drawEnergy() {{
                const c = document.getElementById('uC'); const ctx = c.getContext('2d');
                c.width = c.parentElement.clientWidth; c.height = c.parentElement.clientHeight;
                ctx.clearRect(0,0,c.width,c.height);

                const px=60, py=45, pr=20, pt=35;
                const w = c.width-px-pr, h = c.height-py-pt;

                const rmin = 0.85*r0_eq, rmax = 2.5*r0_eq;
                const yMin = Math.min(U_morse(r0_morse), U_lj(r0_lj)) * 1.25;
                const yMax = Math.abs(yMin) * 0.55;

                const gX = r => px + (r-rmin)/(rmax-rmin)*w;
                const gY = u => pt + (yMax - u)/(yMax - yMin)*h;

                // Axes
                ctx.strokeStyle='#888'; ctx.lineWidth=2; ctx.beginPath();
                ctx.moveTo(px,pt); ctx.lineTo(px,c.height-py); ctx.lineTo(c.width-pr,c.height-py); ctx.stroke();

                // Grid + Y-labels
                ctx.fillStyle='#aaa'; ctx.font='10px sans-serif'; ctx.textAlign='right';
                for (let i=0;i<=5;i++) {{
                    const u = yMin + (yMax-yMin)*i/5; const y = gY(u);
                    ctx.fillText(u.toFixed(3), px-5, y+3);
                    ctx.strokeStyle='#2a2a2a'; ctx.beginPath(); ctx.moveTo(px,y); ctx.lineTo(c.width-pr,y); ctx.stroke();
                }}
                // X-labels
                ctx.textAlign='center';
                for (let i=0;i<=5;i++) {{
                    const r = rmin + (rmax-rmin)*i/5; const x = gX(r);
                    ctx.fillText(r.toFixed(2), x, c.height-py+15);
                }}
                ctx.fillText('r (Å)', px+w/2, c.height-5);
                ctx.save(); ctx.translate(13, pt+h/2); ctx.rotate(-Math.PI/2);
                ctx.fillText('U (eV)', 0, 0); ctx.restore();

                // Zero line
                if (yMin <= 0 && yMax >= 0) {{
                    ctx.strokeStyle='#555'; ctx.lineWidth=1;
                    ctx.beginPath(); ctx.moveTo(px,gY(0)); ctx.lineTo(c.width-pr,gY(0)); ctx.stroke();
                }}

                function plotCurve(fn, color, bold) {{
                    ctx.strokeStyle = color; ctx.lineWidth = bold ? 3 : 2;
                    if (!bold) ctx.setLineDash([4,4]);
                    ctx.beginPath(); let started = false;
                    for (let r=rmin; r<=rmax; r+=(rmax-rmin)/300) {{
                        const u = fn(r);
                        if (u > yMax || u < yMin || !isFinite(u)) {{ started=false; continue; }}
                        if (!started) {{ ctx.moveTo(gX(r),gY(u)); started=true; }} else ctx.lineTo(gX(r),gY(u));
                    }}
                    ctx.stroke(); ctx.setLineDash([]);
                }}

                plotCurve(U_lj,    sel==="lj"    ? '#FF4B4B' : 'rgba(255,75,75,0.30)', sel==="lj");
                plotCurve(U_morse, sel==="morse" ? '#4CAF50' : 'rgba(76,175,80,0.30)', sel==="morse");
                plotCurve(U_harm,  '#FFD700', false);  // harmonic always dashed

                // r0 vertical line
                ctx.strokeStyle='rgba(255,255,255,0.30)'; ctx.lineWidth=1;
                ctx.beginPath(); ctx.moveTo(gX(r0_eq),pt); ctx.lineTo(gX(r0_eq),c.height-py); ctx.stroke();
                ctx.fillStyle='rgba(255,255,255,0.7)'; ctx.font='11px sans-serif'; ctx.textAlign='left';
                ctx.fillText('r₀', gX(r0_eq)+3, pt+12);

                // Current-r marker
                const ucur = U_active(r_cur);
                if (ucur >= yMin && ucur <= yMax) {{
                    ctx.fillStyle='#fff'; ctx.beginPath(); ctx.arc(gX(r_cur),gY(ucur),6,0,Math.PI*2); ctx.fill();
                    ctx.strokeStyle='#000'; ctx.lineWidth=2; ctx.stroke();
                }}

                // Legend
                ctx.font='bold 11px sans-serif'; ctx.textAlign='right';
                ctx.fillStyle = sel==="lj"    ? '#FF4B4B' : 'rgba(255,75,75,0.45)'; ctx.fillText('Lennard-Jones', c.width-pr-5, pt-8);
                ctx.fillStyle = sel==="morse" ? '#4CAF50' : 'rgba(76,175,80,0.45)'; ctx.fillText('Morse',         c.width-pr-5, pt+5);
                ctx.fillStyle = '#FFD700';                                          ctx.fillText('Harmonic ½k(r-r₀)²', c.width-pr-5, pt+18);
            }}

            // ============================================================
            //  FORCE PLOT  F(r) = -dU/dr
            // ============================================================
            function drawForce() {{
                const c = document.getElementById('fC'); const ctx = c.getContext('2d');
                c.width = c.parentElement.clientWidth; c.height = c.parentElement.clientHeight;
                ctx.clearRect(0,0,c.width,c.height);

                const px=60, py=45, pr=20, pt=35;
                const w = c.width-px-pr, h = c.height-py-pt;
                const rmin = 0.85*r0_eq, rmax = 2.5*r0_eq;

                // Y-range from both curves
                let fLo=0, fHi=0;
                for (let r=rmin*1.02; r<=rmax; r+=(rmax-rmin)/100) {{
                    const f1=-dU_lj(r), f2=-dU_morse(r);
                    if (isFinite(f1)) {{ fHi=Math.max(fHi,f1); fLo=Math.min(fLo,f1); }}
                    if (isFinite(f2)) {{ fHi=Math.max(fHi,f2); fLo=Math.min(fLo,f2); }}
                }}
                const yMax = fHi*1.15, yMin = fLo*1.15;

                const gX = r => px + (r-rmin)/(rmax-rmin)*w;
                const gY = f => pt + (yMax - f)/(yMax - yMin)*h;

                // Axes
                ctx.strokeStyle='#888'; ctx.lineWidth=2; ctx.beginPath();
                ctx.moveTo(px,pt); ctx.lineTo(px,c.height-py); ctx.lineTo(c.width-pr,c.height-py); ctx.stroke();
                ctx.strokeStyle='#555'; ctx.beginPath(); ctx.moveTo(px,gY(0)); ctx.lineTo(c.width-pr,gY(0)); ctx.stroke();

                ctx.fillStyle='#aaa'; ctx.font='10px sans-serif'; ctx.textAlign='right';
                for (let i=0;i<=5;i++) {{
                    const f = yMin + (yMax-yMin)*i/5; const y = gY(f);
                    ctx.fillText(f.toFixed(2), px-5, y+3);
                }}
                ctx.textAlign='center';
                for (let i=0;i<=5;i++) {{
                    const r = rmin + (rmax-rmin)*i/5; const x = gX(r);
                    ctx.fillText(r.toFixed(2), x, c.height-py+15);
                }}
                ctx.fillText('r (Å)', px+w/2, c.height-5);
                ctx.save(); ctx.translate(13, pt+h/2); ctx.rotate(-Math.PI/2);
                ctx.fillText('F (eV/Å)', 0, 0); ctx.restore();

                function plotCurve(fn, color, bold) {{
                    ctx.strokeStyle = color; ctx.lineWidth = bold ? 3 : 2;
                    if (!bold) ctx.setLineDash([4,4]);
                    ctx.beginPath(); let started=false;
                    for (let r=rmin; r<=rmax; r+=(rmax-rmin)/300) {{
                        const f = -fn(r);
                        if (!isFinite(f) || f > yMax || f < yMin) {{ started=false; continue; }}
                        if (!started) {{ ctx.moveTo(gX(r),gY(f)); started=true; }} else ctx.lineTo(gX(r),gY(f));
                    }}
                    ctx.stroke(); ctx.setLineDash([]);
                }}
                plotCurve(dU_lj,    sel==="lj"    ? '#FF4B4B' : 'rgba(255,75,75,0.30)', sel==="lj");
                plotCurve(dU_morse, sel==="morse" ? '#4CAF50' : 'rgba(76,175,80,0.30)', sel==="morse");

                // Hooke's law (harmonic): linear segment near r0
                ctx.strokeStyle='#FFD700'; ctx.lineWidth=2; ctx.setLineDash([2,3]);
                const rA=r0_eq*0.92, rB=r0_eq*1.35;
                ctx.beginPath(); ctx.moveTo(gX(rA),gY(F_harm(rA))); ctx.lineTo(gX(rB),gY(F_harm(rB))); ctx.stroke();
                ctx.setLineDash([]);

                // r0 + F=0 markers
                ctx.strokeStyle='rgba(255,255,255,0.30)'; ctx.lineWidth=1;
                ctx.beginPath(); ctx.moveTo(gX(r0_eq),pt); ctx.lineTo(gX(r0_eq),c.height-py); ctx.stroke();

                const fcur = -dU_active(r_cur);
                if (fcur >= yMin && fcur <= yMax) {{
                    ctx.fillStyle='#fff'; ctx.beginPath(); ctx.arc(gX(r_cur),gY(fcur),6,0,Math.PI*2); ctx.fill();
                    ctx.strokeStyle='#000'; ctx.lineWidth=2; ctx.stroke();
                }}

                ctx.font='bold 11px sans-serif'; ctx.textAlign='right'; ctx.fillStyle='#FFD700';
                ctx.fillText("Hooke F = -k(r-r₀)", c.width-pr-5, pt-8);

                // Find max of force (= "ideal strength" of the bond)
                let rPeak = r0_eq, fPeak = -1e9;
                for (let r=r0_eq; r<rmax; r+=0.005) {{
                    const f = -dU_active(r);
                    if (f > fPeak) {{ fPeak = f; rPeak = r; }}
                }}
                if (fPeak > yMin && fPeak < yMax) {{
                    ctx.strokeStyle='rgba(255,165,0,0.6)'; ctx.setLineDash([3,3]);
                    ctx.beginPath(); ctx.moveTo(gX(rPeak),pt); ctx.lineTo(gX(rPeak),c.height-py); ctx.stroke();
                    ctx.setLineDash([]);
                    ctx.fillStyle='rgba(255,165,0,0.85)'; ctx.font='10px sans-serif'; ctx.textAlign='left';
                    ctx.fillText('inflection (max F)', gX(rPeak)+3, pt+12);
                }}
            }}

            // ============================================================
            //  CRYSTAL LATTICE  (FCC/BCC/SC, 2D projection, single bond highlighted)
            // ============================================================
            function drawLattice() {{
                const c = document.getElementById('lC'); const ctx = c.getContext('2d');
                c.width = c.parentElement.clientWidth; c.height = c.parentElement.clientHeight;
                ctx.clearRect(0,0,c.width,c.height);
                ctx.fillStyle='#0a0a0a'; ctx.fillRect(0,0,c.width,c.height);

                const stretch = r_cur / r0_eq;
                const baseDist = Math.min(c.width, c.height) / 6.5;
                const cx = c.width/2, cy = c.height/2;
                const rad = baseDist * 0.30;

                // Build 2D lattice points (t = atom type for rendering)
                const pos = [];
                if (lattice === "FCC") {{
                    // (100) plane projection: corner atoms + face-center atoms
                    for (let i=-3;i<=3;i++) for (let j=-3;j<=3;j++) pos.push({{x:i, y:j, t:0}});
                    for (let i=-3;i<3;i++)  for (let j=-3;j<3;j++)  pos.push({{x:i+0.5, y:j+0.5, t:1}});
                }} else if (lattice === "BCC") {{
                    // (110) plane projection so the body atom is visible
                    for (let i=-3;i<=3;i++) for (let j=-3;j<=3;j++) pos.push({{x:i, y:j, t:0}});
                    for (let i=-3;i<3;i++)  for (let j=-3;j<3;j++)  pos.push({{x:i+0.5, y:j+0.5, t:2}});
                }} else {{
                    for (let i=-3;i<=3;i++) for (let j=-3;j<=3;j++) pos.push({{x:i, y:j, t:0}});
                }}

                // Bonds: connect atoms within nearest-neighbour distance
                ctx.strokeStyle='#444'; ctx.lineWidth=1.5;
                for (let i=0;i<pos.length;i++) for (let j=i+1;j<pos.length;j++) {{
                    const dx = pos[j].x - pos[i].x, dy = pos[j].y - pos[i].y;
                    const d = Math.sqrt(dx*dx+dy*dy);
                    const dmax = (lattice === "SC") ? 1.05 : 0.85;
                    if (d < dmax && d > 0.3) {{
                        ctx.beginPath();
                        ctx.moveTo(cx + pos[i].x*baseDist*stretch, cy + pos[i].y*baseDist*stretch);
                        ctx.lineTo(cx + pos[j].x*baseDist*stretch, cy + pos[j].y*baseDist*stretch);
                        ctx.stroke();
                    }}
                }}

                // Highlight the "active" stretching bond
                let p1, p2;
                if (lattice === "SC") {{ p1 = {{x:0,y:0}};       p2 = {{x:1,y:0}}; }}
                else                   {{ p1 = {{x:0,y:0}};       p2 = {{x:0.5,y:0.5}}; }}

                let hlColor;
                if (stretch > 1.30)      hlColor = '#FF4B4B';   // beyond inflection → bond near breaking
                else if (stretch > 1.10) hlColor = '#FFD700';   // anharmonic regime
                else if (stretch < 0.95) hlColor = '#88CCFF';   // compression
                else                     hlColor = '#4CAF50';   // harmonic / near r0

                ctx.strokeStyle = hlColor; ctx.lineWidth = 5;
                ctx.beginPath();
                ctx.moveTo(cx + p1.x*baseDist*stretch, cy + p1.y*baseDist*stretch);
                ctx.lineTo(cx + p2.x*baseDist*stretch, cy + p2.y*baseDist*stretch);
                ctx.stroke();

                // Atoms
                pos.forEach(p => {{
                    const x = cx + p.x*baseDist*stretch;
                    const y = cy + p.y*baseDist*stretch;
                    if (x < -rad*2 || x > c.width+rad*2 || y < -rad*2 || y > c.height+rad*2) return;
                    const rr = rad * (p.t === 2 ? 0.78 : (p.t === 1 ? 0.88 : 1.00));
                    const grad = ctx.createRadialGradient(x-rr*0.3, y-rr*0.3, rr*0.1, x, y, rr);
                    grad.addColorStop(0,'#FFFFFF');
                    grad.addColorStop(0.3, matColor);
                    grad.addColorStop(1,'#1a1a1a');
                    ctx.fillStyle = grad;
                    ctx.beginPath(); ctx.arc(x, y, rr, 0, Math.PI*2); ctx.fill();
                    ctx.strokeStyle='#222'; ctx.lineWidth=1; ctx.stroke();
                }});

                // Annotations
                ctx.fillStyle='#fff'; ctx.font='bold 13px sans-serif'; ctx.textAlign='left';
                ctx.fillText(lattice + ' lattice', 10, 25);
                ctx.font='11px sans-serif';
                ctx.fillText('r = ' + r_cur.toFixed(3) + ' Å', 10, 45);
                ctx.fillText('r/r₀ = ' + stretch.toFixed(3), 10, 60);
                ctx.font='10px sans-serif'; ctx.fillStyle='rgba(255,255,255,0.6)';
                if (stretch > 1.30)      ctx.fillText('⚠ past inflection — bond fails', 10, 78);
                else if (stretch > 1.10) ctx.fillText('anharmonic — Hooke breaks down', 10, 78);
                else if (stretch < 0.95) ctx.fillText('compression', 10, 78);
                else                     ctx.fillText('harmonic regime ✓', 10, 78);
            }}

            // ============================================================
            //  DASHBOARD + ANIMATION
            // ============================================================
            function updateDashboard() {{
                document.getElementById('val_r').innerText    = r_cur.toFixed(3) + " Å";
                document.getElementById('val_U').innerText    = U_active(r_cur).toFixed(3) + " eV";
                document.getElementById('val_F').innerText    = (-dU_active(r_cur)).toFixed(3) + " eV/Å";
                document.getElementById('val_k').innerText    = k_eq.toFixed(3) + " eV/Å²";
                document.getElementById('val_E').innerText    = E_calc.toFixed(1) + " GPa";
                document.getElementById('val_Eexp').innerText = (Eexp > 0 ? Eexp + " GPa" : "—");
            }}

            function drawAll() {{ drawEnergy(); drawLattice(); drawForce(); updateDashboard(); }}

            function step() {{
                if (!running) return;
                phase += 0.025 * spd;
                // Smooth oscillation: r0 → r0(1+0.45) → r0(1-0.10) → r0, two cycles
                r_cur = r0_eq * (1 + 0.45 * Math.sin(phase) - 0.05*(1 - Math.cos(phase))/2);
                drawAll();
                if (phase > 4*Math.PI) {{
                    running=false; r_cur=r0_eq; phase=0; drawAll();
                    document.getElementById('startBtn3').innerText="▶ Animate Bond Stretch";
                    return;
                }}
                requestAnimationFrame(step);
            }}

            document.getElementById('startBtn3').addEventListener('click', () => {{
                if (running) {{
                    running=false; r_cur=r0_eq; phase=0; drawAll();
                    document.getElementById('startBtn3').innerText="▶ Animate Bond Stretch";
                    return;
                }}
                running=true; phase=0;
                document.getElementById('startBtn3').innerText="⏸ Stop";
                step();
            }});

            drawAll();
            window.addEventListener('resize', () => {{ if (!running) drawAll(); }});
        </script>
    </body></html>
    """

    with col_sim3:
        components.html(html_code_3, height=750, scrolling=False)

    # --- How-to-play guide ---
    with st.expander("🕹️ How to play with this simulator — guided exercises"):
        st.markdown(r"""
**Three live canvases:**
* **U(r) — Energy.**  Both potentials are drawn (the active one bold, the other faded).
  The yellow dashed parabola is the **harmonic approximation**
  $U_{harm} = U(r_0) + \tfrac{1}{2}k(r-r_0)^2$. The white dot tracks your current $r$.
* **Lattice.**  A 2-D projection of the FCC, BCC or SC structure of the chosen element.
  One bond is highlighted: green when in the harmonic regime, yellow when anharmonic
  ($r/r_0 > 1.10$), red past the inflection point ($r/r_0 > 1.30$ — the bond is failing),
  blue under compression.
* **F(r).**  The force = −dU/dr. The yellow dashed segment is Hooke's
  linear approximation; the orange vertical line marks the **inflection of $U$ = peak of $F$**,
  i.e. the *theoretical bond strength*.

**The dashboard reports** $r$, $U(r)$, $F(r)$, the curvature $k = \partial^2 U/\partial r^2|_{r_0}$,
the Young's modulus calculated from $E = k/r_0 \times 160.218$ (eV/Å² → GPa), and the
experimental $E$ for comparison.

**Exercise 1 — change a Morse parameter, watch $E$.**
Pick *Copper*, *Morse*, then drag the well depth $D$ from 0.34 → 1.0 eV.
The dashboard $E$ scales linearly because $k = 2D\alpha^2$, so $E \propto D$.
Check: triple $D$ ⇒ $E$ triples.

**Exercise 2 — anharmonicity.**
Set Copper / Morse, press **▶ Animate Bond Stretch**. The atom oscillates from compression
through equilibrium out to $r/r_0 \approx 1.45$. Watch the white dot leave the yellow
parabola — that is anharmonicity. In real crystals this is responsible for thermal expansion
(asymmetric well = mean-distance grows with $T$) and for the temperature dependence of $E$.

**Exercise 3 — switch to LJ, see why it over-predicts $E$.**
Same element (Copper). Toggle to *Lennard-Jones (12-6)*. Note that the LJ curve is
*steeper* near $r_0$ — its $r^{-12}$ repulsion is too stiff. The calculated $E$ is too high
by 1.5–2.5×. Morse, with its softer exponential repulsion, is the better physical model.

**Exercise 4 — ideal strength of a bond.**
Look at the F(r) panel. The maximum (orange dashed line) is the *ideal* tensile strength:
the stress at which a perfect crystal of this element would fracture by uniform bond
breaking. It is roughly $E/10$. Real metals fail at $\sim E/100$ — the gap that
dislocations explain (see Tab ⚛️ Defects).

**Exercise 5 — predict $E$ for an unfamiliar element.**
Tungsten has a deep, narrow well ($D \approx 1$ eV, $\alpha \approx 1.4$).
Compute $k = 2D\alpha^2 \approx 4$ eV/Å² and $E \approx (4/2.74)\times 160 \approx 234$ GPa.
Check the simulator — the $E_{calc}$ value should land near 230 GPa (experimental: 411 GPa,
the gap is the missing many-body / d-band physics).
""")

    with st.expander("📐 Worked exercises with formulas — solve these by hand"):
        st.markdown(r"""
The Young's modulus is the curvature of $U(r)$ at the equilibrium bond length, divided by $r_0$.
Once you internalize that, every problem below is a one-liner.

**Useful unit conversions.**
- $1\;\text{eV} = 1.602\times 10^{-19}\;\text{J}$
- $1\;\text{Å} = 10^{-10}\;\text{m}$
- $1\;\text{eV/Å}^2 = 16.02\;\text{N/m}$ (memorize this — it converts every problem to SI)

**Master formula (1-D bond, simple-cubic packing).**
$$E \approx \frac{k}{r_0} \quad\text{where}\quad k = \left.\frac{d^2U}{dr^2}\right|_{r=r_0}$$

---

### Exercise 1 — Morse $E$ for copper, from scratch
Cu Morse parameters: $D = 0.34$ eV, $\alpha = 1.36$ Å$^{-1}$, $r_0 = 2.55$ Å.

**Formula.** Differentiate the Morse potential $U(r) = D\big(1 - e^{-\alpha(r-r_0)}\big)^2 - D$ twice, evaluate at $r=r_0$:
$$k_{\text{Morse}} = 2D\alpha^{2}$$

**Solution.**
- $k = 2 \times 0.34 \times 1.36^2 = 2 \times 0.34 \times 1.85 = 1.258\;\text{eV/Å}^2$
- Convert: $k = 1.258 \times 16.02 = 20.15\;\text{N/m}$
- Convert $r_0 = 2.55$ Å $= 2.55\times 10^{-10}$ m
- $E \approx k/r_0 = 20.15/(2.55\times 10^{-10}) = 7.9\times 10^{10}\;\text{Pa} = \mathbf{79\;\text{GPa}}$

> Experimental Cu: 130 GPa. The model **under-predicts** by ~40 % because the 1-D bond approximation
> ignores the 3-D + many-body nature of metallic bonding. **Direction of error matters: Morse always
> under-predicts metals.**

---

### Exercise 2 — Predict $E$ for tungsten
Typical W parameters: $D = 0.90$ eV, $\alpha = 1.40$ Å$^{-1}$, $r_0 = 2.74$ Å.

**Solution.**
- $k = 2 \times 0.90 \times 1.40^2 = 3.528\;\text{eV/Å}^2 = 56.5\;\text{N/m}$
- $E = 56.5/(2.74\times 10^{-10}) = 2.06\times 10^{11}\;\text{Pa} = \mathbf{206\;\text{GPa}}$

> Experimental W: 411 GPa. Ratio $E_{calc}/E_{exp} = 0.50$ — same factor-of-two under-prediction as Cu.
> The trend is captured even though the absolute number is off.

---

### Exercise 3 — LJ $E$ for the same copper, see the over-prediction
The Lennard-Jones 12-6 potential reaches its minimum at $r_0 = 2^{1/6}\sigma_{LJ}$ with depth $\varepsilon_{LJ}$.
Differentiate twice, evaluate at $r_0$:
$$k_{LJ} = \frac{72\,\varepsilon_{LJ}}{r_0^{2}}$$

For Cu: $\varepsilon_{LJ} = 0.34$ eV, $r_0 = 2.55$ Å.

**Solution.**
- $k_{LJ} = 72 \times 0.34/2.55^2 = 24.48/6.50 = 3.766\;\text{eV/Å}^2 = 60.3\;\text{N/m}$
- $E = 60.3/(2.55\times 10^{-10}) = 2.37\times 10^{11}\;\text{Pa} = \mathbf{237\;\text{GPa}}$

> Compare to Ex 1: $E_{LJ}/E_{Morse} = 237/79 = 3.0\times$ stiffer. **LJ over-predicts $E$ for Cu by a factor of ~2**
> over experiment. The reason: the $r^{-12}$ repulsion is too short-ranged, sharpening the well excessively.

---

### Exercise 4 — Ideal tensile strength of a single bond
For Morse, $F(r) = -dU/dr$ peaks at $r_m = r_0 + \ln(2)/\alpha$, and
$$F_{\max} = \frac{D\,\alpha}{2}$$

For Cu ($D = 0.34$ eV, $\alpha = 1.36$ Å$^{-1}$):

**Solution.**
- $F_{\max} = 0.34 \times 1.36 / 2 = 0.2312\;\text{eV/Å}$
- Convert: $F_{\max} = 0.2312 \times 1.602\times 10^{-19}/10^{-10} = 3.7\times 10^{-10}\;\text{N}$ per bond
- Bond cross-section $\approx r_0^2 = (2.55\times 10^{-10})^2 = 6.5\times 10^{-20}\;\text{m}^2$
- $\sigma_{\text{ideal}} = F_{\max}/A = 3.7\times 10^{-10}/6.5\times 10^{-20} = 5.7\times 10^{9}\;\text{Pa} = \mathbf{5.7\;\text{GPa}}$

> Compare to Cu's experimental yield $\sigma_y \approx 50$ MPa — **100× lower than ideal.**
> That gap is the entire reason dislocations were postulated (Orowan, Polanyi, Taylor 1934).

---

### Exercise 5 — Strain at the inflection point ("end of harmonic regime")
The Morse potential has its inflection ($d^2U/dr^2 = 0$) at exactly $r_{infl} = r_0 + \ln(2)/\alpha$.

For Cu: $r_{infl} = 2.55 + 0.693/1.36 = 2.55 + 0.510 = \mathbf{3.06\;\text{Å}}$.

Strain at the inflection: $\varepsilon_{infl} = (r_{infl} - r_0)/r_0 = 0.510/2.55 = \mathbf{0.20\;(20\%)}$.

> Hooke's law (linear elasticity) really starts to break down by $\sim 5$–10 % strain;
> by 20 % strain you've passed the maximum slope and the bond is effectively "broken" —
> consistent with the simulator highlighting "anharmonic" above $r/r_0 = 1.10$ and "bond fails"
> above $1.30$.

---

### Exercise 6 — From bond stiffness to phonon frequency
The vibrational frequency of a diatomic bond is $\nu = \tfrac{1}{2\pi}\sqrt{k/\mu}$, where $\mu$ is
the reduced mass.

For Cu–Cu: $m_{Cu} = 63.5\;\text{amu} = 1.054\times 10^{-25}$ kg, so $\mu = m/2 = 5.27\times 10^{-26}$ kg.
With $k = 20.15$ N/m (from Ex 1):

**Solution.**
- $\nu = (1/2\pi)\sqrt{20.15/5.27\times 10^{-26}} = (1/2\pi)\sqrt{3.82\times 10^{26}}$
- $\nu = (1/2\pi)(1.96\times 10^{13}) = \mathbf{3.1\;\text{THz}}$

> Cu's measured Debye frequency is $\nu_D \approx 7$ THz — same order of magnitude. The pair-potential
> bond is not just an arithmetic toy: it correctly predicts the **time scale** of atomic vibrations.

---

### Exercise 7 — Why the LJ over-prediction grows with hardness
The ratio $k_{LJ}/k_{\text{Morse}} = (72\,\varepsilon/r_0^2)/(2D\alpha^2)$. Setting $D = \varepsilon$:
$$\frac{k_{LJ}}{k_{\text{Morse}}} = \frac{36}{(\alpha r_0)^{2}}$$

For most metals $\alpha r_0$ falls in the range 3.0–4.5, giving ratios from $\sim 4$ down to $\sim 1.8$.

**Take-away.** The "stiffer" the actual bond ($\alpha r_0$ larger), the smaller the LJ over-prediction.
Which is why **LJ is a passable model for noble gases** (where $\alpha r_0 \to$ large because the well
is narrow) but a poor one for metals.
""")

    # ---- Hidden bonus exercise (gated) ----
    hidden_exercise(
        key_prefix="t5_bonus",
        title="🔒 Hidden bonus exercise — only opens once you've memorized the key conversion factor",
        gate_question=(
            r"What is the conversion factor $1\;\text{eV/Å}^2 = \;?\;\text{N/m}$? "
            "(Numerical value with **two decimal places**.)"
        ),
        hint="It's stated explicitly in the master-formula block of Worked Exercise 1.",
        accepted_answers=["16.02", "16.0", "16", "16.03", "16.01", "16.022"],
        numeric_target=16.02,
        numeric_tolerance=0.10,
        exercise_md=r"""
### 🏆 Bonus — Predict $E$ for diamond and watch the model **flip**

Carbon–carbon $sp^3$ covalent bond in diamond:
$D \approx 3.6$ eV (very deep), $\alpha \approx 2.0$ Å$^{-1}$ (very narrow well), $r_0 \approx 1.54$ Å.

**Problem.**
(i) Compute the bond stiffness $k = 2D\alpha^{2}$ in both eV/Å² and N/m.

(ii) Use $E \approx k/r_0$ to predict $E_{\text{calc}}$ in GPa.

(iii) Compare to experimental diamond $E_{\text{exp}} \approx 1050$ GPa.

(iv) **Surprise question:** Was the predicted $E$ above or below the experimental value?
Why does the model flip direction (under-predict → over-predict) when going from copper to diamond?

---

**Solution.**
- (i) $k = 2 \times 3.6 \times 4 = 28.8\;\text{eV/Å}^2 = 28.8 \times 16.02 = \mathbf{461\;\text{N/m}}$
- (ii) $E = 461/(1.54\times 10^{-10}) = 3.0\times 10^{12}\;\text{Pa} = \mathbf{3000\;\text{GPa}}$
- (iii) Experimental: 1050 GPa. Ratio $E_{\text{calc}}/E_{\text{exp}} \approx \mathbf{2.85}$ — the
  1-D bond model **over-predicts diamond by nearly 3×**. (Cu, by contrast, was *under*-predicted
  by ~40 % — see Worked Ex 1.)

> **Why does the direction flip?**
> - For **metals** (Cu, W, ...) the simple 1-D bond model misses the *delocalized, many-body*
>   nature of metallic bonding — the "electron sea" actually contributes more stiffness than
>   a pair potential can capture, so $E_{\text{calc}} < E_{\text{exp}}$.
> - For **covalent solids** (diamond, Si) each atom forms only **4** strong directional bonds
>   at $109.5^\circ$ — not the 6 nearest neighbours of a simple-cubic packing assumed by our
>   $E \approx k/r_0$ formula. Counting all 6 axial bonds at full stiffness over-counts the
>   actual load-carrying connectivity, so $E_{\text{calc}} > E_{\text{exp}}$.
>
> The corrected formula uses a **structure factor** $\xi$ that depends on coordination and bond geometry:
> $E = \xi \cdot k/r_0$. For diamond cubic, $\xi \approx 1/3$ — bringing $E_{\text{calc}}$ down to ~1000 GPa,
> matching experiment. **The pair-potential is correct in scaling but needs the right geometric prefactor.**
""",
    )

    # --- Comparison plot: E_calc (LJ vs Morse) vs E_exp ---
    st.subheader("📊 How well do pair potentials predict $E$?")
    elements_cmp = []
    for name, ad_ in atomic_db.items():
        if ad_["E_exp"] == 0:
            continue
        # Morse
        Dm, am_, r0m = ad_["morse"]["D"], ad_["morse"]["a"], ad_["morse"]["r0"]
        k_morse = 2.0 * Dm * am_ * am_
        E_morse_GPa = (k_morse / r0m) * 160.218
        # LJ
        eps_, sig_ = ad_["lj"]["eps"], ad_["lj"]["sigma"]
        r0_lj = sig_ * (2.0 ** (1.0/6.0))
        k_lj = (57.146 * eps_) / (sig_ * sig_)   # closed-form curvature at r0
        E_lj_GPa = (k_lj / r0_lj) * 160.218
        elements_cmp.append((name.split(" ")[0], ad_["E_exp"], E_morse_GPa, E_lj_GPa, ad_["lattice"]))

    fig_cmp, ax_cmp = plt.subplots(figsize=(8.5, 4.6))
    e_exp_arr   = np.array([e[1] for e in elements_cmp])
    e_morse_arr = np.array([e[2] for e in elements_cmp])
    e_lj_arr    = np.array([e[3] for e in elements_cmp])
    labels      = [e[0] for e in elements_cmp]

    ax_cmp.plot([0, 500], [0, 500], '--', color="#888", lw=1.2, label="ideal $E_{calc}=E_{exp}$")
    ax_cmp.scatter(e_exp_arr, e_morse_arr, s=110, color="#4CAF50", edgecolor='white', lw=1.0, label="Morse")
    ax_cmp.scatter(e_exp_arr, e_lj_arr,    s=110, color="#FF4B4B", edgecolor='white', lw=1.0, label="Lennard-Jones")
    for x, y, lbl in zip(e_exp_arr, e_morse_arr, labels):
        ax_cmp.annotate(lbl, (x, y), textcoords="offset points", xytext=(7, 4),
                        fontsize=9, color="#cccccc")
    ax_cmp.set_xlabel("Experimental Young's modulus $E_{exp}$ (GPa)")
    ax_cmp.set_ylabel("Calculated Young's modulus $E_{calc} = (k/r_0)\\times 160.218$ (GPa)")
    ax_cmp.set_title("Pair-potential prediction of $E$: Morse vs Lennard-Jones")
    ax_cmp.set_xlim(0, max(e_exp_arr.max(), e_lj_arr.max()) * 1.10)
    ax_cmp.set_ylim(0, max(e_exp_arr.max(), e_lj_arr.max()) * 1.10)
    ax_cmp.grid(True, alpha=0.3)
    ax_cmp.legend(loc='upper left')
    fig_cmp.tight_layout()
    st.pyplot(fig_cmp, width="stretch")
    plt.close(fig_cmp)

    st.caption("""
    The dashed line is the perfect-prediction reference. Morse (green) lands close to it
    for FCC metals; LJ (red) systematically overshoots — a direct consequence of the
    too-stiff $r^{-12}$ repulsion. For BCC tungsten, both potentials under-predict
    because the strong d-band (many-body) bonding is invisible to a pair potential.
    """)

    with st.expander("📚 Theory: how E emerges from U(r) — full derivation"):
        st.markdown(r"""
**The chain of logic:**

1. **Equilibrium condition.** At the bond length $r_0$, the potential energy $U(r)$ is at a minimum, so $\partial U/\partial r |_{r_0} = 0$. Both LJ and Morse satisfy this by construction.

2. **Bond stiffness from curvature.** Expanding $U(r)$ in a Taylor series around $r_0$ and keeping only the leading non-vanishing term:

$$U(r) \approx U(r_0) + \tfrac{1}{2}\,k_\text{bond}\,(r-r_0)^2,\qquad k_\text{bond} = \left.\frac{\partial^2 U}{\partial r^2}\right|_{r_0}$$

This is the **harmonic approximation** — the bond behaves like a tiny spring of stiffness $k_\text{bond}$ for small displacements.

3. **From bond stiffness to Young's modulus** (1D atomic chain estimate):
   - Force per bond: $F = -k_\text{bond}(r-r_0)$
   - Stress: $\sigma = F/A_0$ where $A_0 \sim r_0^2$ is the cross-sectional area per atom
   - Strain: $\varepsilon = (r-r_0)/r_0$
   - Hooke's law for the solid: $\sigma = E\,\varepsilon$ ⇒ **$E = k_\text{bond} / r_0$**

4. **Numerical conversion:** $E\,[\text{GPa}] = (k\,[\text{eV/Å}^2] / r_0\,[\text{Å}]) \times 160.218$.

**Closed-form curvatures at $r_0$:**

| Potential | $r_0$ | $k_\text{bond} = \partial^2 U/\partial r^2 \big|_{r_0}$ |
|-----------|-----|-------|
| Lennard-Jones | $2^{1/6}\sigma$ | $72\,\varepsilon / (2^{1/3}\sigma^2) \approx 57.146\,\varepsilon/\sigma^2$ |
| Morse | parameter $r_0$ | $2D\alpha^2$ |

**Why LJ and Morse disagree:**
- LJ's $r^{-12}$ repulsion makes the curvature at $r_0$ steeper than reality → **over-predicts $E$** by 1.5–2.5×.
- Morse's exponential repulsion is gentler → **under-predicts $E$** by 0.4–0.8×.
- The harmonic parabola hugs both curves at $r_0$ but diverges fast — this is why elasticity stays linear only for small strain, and why metals can exhibit anharmonic effects (thermal expansion, elastic-modulus temperature dependence) at higher T.

**Why $E_\text{calc} \neq E_\text{exp}$ exactly even with a "good" potential:**
- The 1D-chain formula ignores the lattice geometry. A real FCC or BCC crystal has multiple bond directions, and the proper expression involves a **lattice sum** over neighbours, with direction-dependent factors.
- Pair potentials miss angular bonding (critical for covalent solids like Si or diamond, where the directional sp³ bonds set the modulus).
- These are 0 K calculations; real $E$ is measured at room temperature where anharmonicity softens the effective stiffness by a few percent.
- Many-body effects (electron sea in metals) are absent — that's why EAM and tight-binding potentials do better than pair potentials for metals.

**The "ideal strength" — the inflection point on F(r):**
The force $F(r) = -\partial U/\partial r$ has a maximum at the inflection point of $U(r)$, marked on the F-plot. This is the theoretical maximum stress a bond can sustain before snapping — typically around $E/10$ in real materials, but considerably higher in this simple model because real solids fail by dislocation motion (in metals) or crack growth (in ceramics) long before bonds reach their ideal limit.
""")

# ==========================================
# TAB 6: FINAL ASSESSMENT
# ==========================================
with tab6:
    st.header("📝 Final Assessment")
    st.markdown("""
    Test your understanding of the materials engineering concepts covered in this module.
    Below are **three real stress–strain curves** drawn with matplotlib at engineering
    scale, with grid lines and key features annotated. Use them to answer the
    curve-analysis questions that follow.
    """)

    # ============================================================
    # Real engineering-style stress–strain plots (matplotlib)
    # ============================================================
    def make_curve_A():
        """Ductile metal: E=100 GPa, YS=400, UTS=600, fracture at ε=0.15."""
        eps = np.concatenate([
            np.linspace(0.0,    0.004, 30),    # elastic
            np.linspace(0.004,  0.020, 30),    # yield plateau / early plastic
            np.linspace(0.020,  0.10,  60),    # strain hardening to UTS
            np.linspace(0.10,   0.15,  40),    # post-UTS softening to fracture
        ])
        sig = np.zeros_like(eps)
        for i, e in enumerate(eps):
            if e <= 0.004:
                sig[i] = 100000.0 * e          # E = 100 GPa
            elif e <= 0.020:
                t = (e - 0.004) / (0.020 - 0.004)
                sig[i] = 400 + (500 - 400) * t
            elif e <= 0.10:
                t = (e - 0.020) / (0.10 - 0.020)
                sig[i] = 500 + (600 - 500) * (t ** 0.4)
            else:
                t = (e - 0.10) / (0.15 - 0.10)
                sig[i] = 600 - 100 * t
        return eps, sig

    def make_curve_B():
        """Lower-strength metal: E=10 GPa, YS=200, UTS=250, fracture at ε=0.20."""
        eps = np.concatenate([
            np.linspace(0.0,   0.020, 30),     # elastic
            np.linspace(0.020, 0.10,  60),     # strain hardening
            np.linspace(0.10,  0.20,  40),     # post-UTS softening
        ])
        sig = np.zeros_like(eps)
        for i, e in enumerate(eps):
            if e <= 0.020:
                sig[i] = 10000.0 * e           # E = 10 GPa
            elif e <= 0.10:
                t = (e - 0.020) / (0.10 - 0.020)
                sig[i] = 200 + (250 - 200) * (t ** 0.5)
            else:
                t = (e - 0.10) / (0.20 - 0.10)
                sig[i] = 250 - 50 * t
        return eps, sig

    def make_curve_C():
        """Brittle ceramic: E=300 GPa, linear-elastic, brittle fracture at ε=0.001 → σ=300 MPa."""
        eps = np.linspace(0.0, 0.001, 50)
        sig = 300000.0 * eps
        return eps, sig

    epsA, sigA = make_curve_A()
    epsB, sigB = make_curve_B()
    epsC, sigC = make_curve_C()

    fig_q, axs = plt.subplots(1, 3, figsize=(13.5, 4.4))

    # --- Material A ---
    axA = axs[0]
    axA.plot(epsA, sigA, color="#4CAF50", lw=2.4, label="σ(ε)")
    axA.plot([0, 0.004], [0, 400], color="#FFD700", ls=":", lw=1.5)  # elastic continuation
    axA.scatter([0.004], [400], s=70, color="#FFD700", zorder=5, ec='white', lw=0.8)
    axA.scatter([0.10],  [600], s=70, color="#FF6F00", zorder=5, ec='white', lw=0.8)
    axA.scatter([0.15],  [500], s=70, color="#FF4B4B", zorder=5, ec='white', lw=0.8)
    axA.annotate("Yield",     xy=(0.004, 400), xytext=(0.025, 350),
                 fontsize=9, color="#FFD700",
                 arrowprops=dict(arrowstyle="->", color="#FFD700", lw=1))
    axA.annotate("UTS",       xy=(0.10,  600), xytext=(0.05, 660),
                 fontsize=9, color="#FF6F00",
                 arrowprops=dict(arrowstyle="->", color="#FF6F00", lw=1))
    axA.annotate("Fracture",  xy=(0.15,  500), xytext=(0.115, 410),
                 fontsize=9, color="#FF4B4B",
                 arrowprops=dict(arrowstyle="->", color="#FF4B4B", lw=1))
    axA.set_xlim(0, 0.16); axA.set_ylim(0, 700)
    axA.set_xticks(np.arange(0, 0.17, 0.02))
    axA.set_yticks(np.arange(0, 701, 100))
    axA.grid(True, which='both', alpha=0.35)
    axA.set_xlabel(r"Strain $\varepsilon$")
    axA.set_ylabel(r"Stress $\sigma$ (MPa)")
    axA.set_title("Material A — ductile alloy")

    # --- Material B ---
    axB = axs[1]
    axB.plot(epsB, sigB, color="#FF4B4B", lw=2.4)
    axB.plot([0, 0.020], [0, 200], color="#FFD700", ls=":", lw=1.5)
    axB.scatter([0.020], [200], s=70, color="#FFD700", zorder=5, ec='white', lw=0.8)
    axB.scatter([0.10],  [250], s=70, color="#FF6F00", zorder=5, ec='white', lw=0.8)
    axB.scatter([0.20],  [200], s=70, color="#FF4B4B", zorder=5, ec='white', lw=0.8)
    axB.annotate("Yield",     xy=(0.020, 200), xytext=(0.05, 130),
                 fontsize=9, color="#FFD700",
                 arrowprops=dict(arrowstyle="->", color="#FFD700", lw=1))
    axB.annotate("UTS",       xy=(0.10,  250), xytext=(0.06, 280),
                 fontsize=9, color="#FF6F00",
                 arrowprops=dict(arrowstyle="->", color="#FF6F00", lw=1))
    axB.annotate("Fracture",  xy=(0.20,  200), xytext=(0.155, 130),
                 fontsize=9, color="#FF4B4B",
                 arrowprops=dict(arrowstyle="->", color="#FF4B4B", lw=1))
    axB.set_xlim(0, 0.21); axB.set_ylim(0, 300)
    axB.set_xticks(np.arange(0, 0.22, 0.05))
    axB.set_yticks(np.arange(0, 301, 50))
    axB.grid(True, which='both', alpha=0.35)
    axB.set_xlabel(r"Strain $\varepsilon$")
    axB.set_ylabel(r"Stress $\sigma$ (MPa)")
    axB.set_title("Material B — softer ductile metal")

    # --- Material C ---
    axC = axs[2]
    axC.plot(epsC * 1000, sigC, color="#88CCFF", lw=2.4)
    axC.scatter([1.0], [300], s=70, color="#FF4B4B", zorder=5, ec='white', lw=0.8)
    axC.annotate("Brittle\nfracture", xy=(1.0, 300), xytext=(0.55, 200),
                 fontsize=9, color="#FF4B4B",
                 arrowprops=dict(arrowstyle="->", color="#FF4B4B", lw=1))
    axC.set_xlim(0, 1.1); axC.set_ylim(0, 350)
    axC.set_xticks(np.arange(0, 1.2, 0.2))
    axC.set_yticks(np.arange(0, 351, 50))
    axC.grid(True, which='both', alpha=0.35)
    axC.set_xlabel(r"Strain $\varepsilon$  (×10$^{-3}$)")
    axC.set_ylabel(r"Stress $\sigma$ (MPa)")
    axC.set_title("Material C — brittle ceramic")

    fig_q.tight_layout()
    st.pyplot(fig_q, width="stretch")
    plt.close(fig_q)

    st.caption(
        "Reference values for the questions below — read them off the gridded axes:  "
        "**Material A**: $E$ slope to (0.004, 400); UTS at (0.10, 600); fracture at (0.15, 500). "
        "**Material B**: yield at (0.020, 200); UTS at (0.10, 250); fracture at (0.20, 200). "
        "**Material C**: linear-elastic to (0.001, 300), then brittle."
    )

    st.divider()

    with st.form("quiz_form"):
        st.subheader("Theoretical Knowledge")
        q1 = st.radio("1. If a material's stress–strain curve does not show a clear yield point, which standardized method is used to determine Yield Strength?",
                      options=["A) 0.5% Offset Method", "B) Ultimate Peak Method", "C) 0.2% Offset Method", "D) Tangent Modulus Method"],
                      index=None)

        q2 = st.radio("2. Why does 'strain hardening' occur during plastic deformation?",
                      options=["A) Because dislocation movement is blocked and entangled, requiring more stress to continue.",
                               "B) Because the material is returning to its elastic state.",
                               "C) Because the atomic bonds become inherently stiffer.",
                               "D) Because dislocations are completely eliminated."],
                      index=None)

        q3 = st.radio("3. According to the Hall–Petch relationship, what happens when you decrease the average grain size of a metal?",
                      options=["A) The yield strength decreases", "B) The yield strength increases",
                               "C) The Young's Modulus increases", "D) It turns into a ceramic"],
                      index=None)

        q4 = st.radio("4. How is macroscopic stiffness (Young's Modulus) related to the interatomic potential energy curve U(r)?",
                      options=["A) It relates to the total area under the curve.",
                               "B) It is the exact lowest point of the curve.",
                               "C) It relates to the second derivative (curvature) at the minimum.",
                               "D) It relates to the first derivative (slope) at the minimum."],
                      index=None)

        q5 = st.radio("5. What exactly is a 'dislocation' in material science?",
                      options=["A) A missing atom in the structure", "B) A crack on the surface",
                               "C) A planar boundary between grains", "D) A 1-D line defect in the crystal lattice"],
                      index=None)

        q6 = st.radio("6. Why do grain boundaries make a metal stronger?",
                      options=["A) They act as massive roadblocks that stop dislocation movement.",
                               "B) They add chemical impurities to the lattice.",
                               "C) They make the atomic bonds inherently stiffer.",
                               "D) They absorb thermal energy."],
                      index=None)

        st.subheader("Curve Analysis (refer to the three plots above)")

        q7 = st.radio("7. From **Material A**, what is the approximate Young's Modulus $E$ from the linear elastic region?",
                      options=["A) 50,000 MPa", "B) 100,000 MPa", "C) 150,000 MPa", "D) 200,000 MPa"],
                      index=None)

        q8 = st.radio("8. From **Material A**, what is the Ultimate Tensile Strength (UTS)?",
                      options=["A) 400 MPa", "B) 500 MPa", "C) 600 MPa", "D) 700 MPa"],
                      index=None)

        q9 = st.radio("9. From **Material B**, at what stress does yielding (YS) approximately occur?",
                      options=["A) 100 MPa", "B) 150 MPa", "C) 200 MPa", "D) 250 MPa"],
                      index=None)

        q10 = st.radio("10. From **Material C**, what statement best describes its mechanical behaviour?",
                       options=["A) Highly ductile with a long plastic plateau",
                                "B) Linear-elastic to brittle fracture; no plastic regime",
                                "C) Superelastic with hysteresis on unloading",
                                "D) Strain-hardens to twice the yield stress before fracture"],
                       index=None)

        submit_btn = st.form_submit_button("Submit Answers")

        if submit_btn:
            answers = {
                "Q1":  ("C", q1, "The 0.2 % offset method (ASTM E8 / ISO 6892-1) draws a line parallel to the elastic slope, shifted by ε = 0.002."),
                "Q2":  ("A", q2, "Plastic deformation multiplies and tangles dislocations. Their mutual interactions raise the flow stress — Taylor's relation $\\sigma_y \\propto Gb\\sqrt{\\rho}$."),
                "Q3":  ("B", q3, "Hall–Petch: $\\sigma_y = \\sigma_0 + k_y/\\sqrt{d}$. Smaller $d$ ⇒ more boundaries per volume ⇒ more obstacles to dislocations ⇒ higher $\\sigma_y$."),
                "Q4":  ("C", q4, "$E \\approx (1/r_0)\\,\\partial^2 U/\\partial r^2|_{r_0}$. Stiffness is the *curvature* of $U(r)$ at the equilibrium bond length."),
                "Q5":  ("D", q5, "Dislocations are 1-D *line* defects (edge or screw). Vacancies are 0-D, grain boundaries are 2-D."),
                "Q6":  ("A", q6, "Grain boundaries block gliding dislocations. The next grain has different crystallographic orientation, so slip cannot continue without higher stress."),
                "Q7":  ("B", q7, "Slope = 400 MPa / 0.004 = **100,000 MPa = 100 GPa** in the elastic region."),
                "Q8":  ("C", q8, "Peak of the curve = **600 MPa**, reached at ε = 0.10."),
                "Q9":  ("C", q9, "Material B yields at the end of its linear segment, at (ε = 0.020, σ = **200 MPa**)."),
                "Q10": ("B", q10, "Material C is the ceramic: the curve is a perfectly straight line up to ε = 0.001 with no plasticity, then snaps."),
            }

            score = sum(1 for (correct, given, _) in answers.values()
                        if given is not None and given.startswith(correct + ")"))

            st.success(f"You scored **{score} / 10**.")
            if score == 10:
                st.balloons()

            st.markdown("### 📋 Detailed feedback")
            for qkey, (correct, given, explanation) in answers.items():
                if given is None:
                    st.warning(f"**{qkey} — not answered.** Correct answer: **{correct})**.  *{explanation}*")
                elif given.startswith(correct + ")"):
                    st.success(f"**{qkey} ✓** Your answer: {given}.  *{explanation}*")
                else:
                    st.error(f"**{qkey} ✗** You chose: {given}. Correct: **{correct})**.  *{explanation}*")
