REMOTE="pwr-remote:lorawan-th-sensor/"

rclone sync .env "$REMOTE"
rclone sync src/config.h "$REMOTE"

RESOURCE=$(rclone link "$REMOTE")
echo "$RESOURCE"
