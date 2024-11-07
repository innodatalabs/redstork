# exit on error and do long report
set -eux

REDSTORK_ROOT=${REDSTORK_ROOT:-.}


. $REDSTORK_ROOT/steps/00-env.sh
$REDSTORK_ROOT/steps/01-install.sh
$REDSTORK_ROOT/steps/02-checkout.sh
$REDSTORK_ROOT/steps/03-patch.sh
$REDSTORK_ROOT/steps/04-install-extra.sh
$REDSTORK_ROOT/steps/05-configure.sh
$REDSTORK_ROOT/steps/06-build.sh
$REDSTORK_ROOT/steps/07-stage.sh
$REDSTORK_ROOT/steps/08-wheel.sh
