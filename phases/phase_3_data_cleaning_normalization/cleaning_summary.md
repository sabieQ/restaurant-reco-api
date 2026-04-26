# Cleaning Summary

- Dataset: `ManikaSaini/zomato-restaurant-recommendation` (`zomato.csv`)
- Raw rows: `51717`
- Rows after required text fields: `51717`
- Rows after numeric presence filter: `51618`
- Retention: `99.81%`
- P0 over-aggressive cleaning: `pass`
- P0 incorrect budget mapping: `pass`

## Canonical Mapping
- `restaurant_name` -> `name`
- `location` -> `location`
- `cuisine` -> `cuisines`
- `average_cost_for_two` -> `approx_cost(for two people)`
- `rating` -> `rate`
