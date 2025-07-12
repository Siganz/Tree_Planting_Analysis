"""Global constants for the STP package, pulled from config."""

from config import get_constant

DEFAULT_EPSG = get_constant('epsg.default', 4326)
NYSP_EPSG = get_constant('epsg.nysp', 2263)

# TODO: All done! No more hardcodes—constants now come from defaults.yaml.
# Remove this file later if you want to access directly via get_constant everywhere.