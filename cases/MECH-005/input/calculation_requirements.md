# Thermal Expansion Calculation Requirements - Synthetic

Calculate the unconstrained thermal expansion of the component.

Requirements:

- Calculate temperature change as operating temperature minus installation
  temperature.
- Use the linear thermal expansion equation:
  delta_L = alpha * L * delta_T
- Report free expansion in millimetres.
- Independently verify the result using the installed length converted to
  millimetres before applying the equation.
- Report the relative difference between the primary and verification results.
- Identify whether the component increases or decreases in length.
- Use the disposition `requires_expansion_accommodation_review` when positive
  thermal expansion exists.
- Do not approve the final support, flexibility, stress, or restraint design.
- All outputs require qualified human review.
