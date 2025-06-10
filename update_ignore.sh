#!/bin/sh

if [ ! -f "ccfddl.1h.py" ]; then
    echo "Error: 'ccfddl.1h.py' does not exist in the current directory."
    exit 1
fi

CURRENT_DIR=$(basename "$(pwd)")

TEMP_FILE=$(mktemp)

find . -type f -not -path "./ccfddl.1h.py" -not -path "./.*" | sed "s|^\./|$CURRENT_DIR/|" > "$TEMP_FILE"

if [ ! -f "../.swiftbarignore" ]; then
    touch "../.swiftbarignore"
    echo "Created new .swiftbarignore file in parent directory."
fi

echo "" >> "../.swiftbarignore"
echo "# swiftbar-ccfddl" >> "../.swiftbarignore"
cat "$TEMP_FILE" >> "../.swiftbarignore"

rm "$TEMP_FILE"

echo "Successfully updated ../.swiftbarignore with files to ignore."
echo "Total files added to ignore list: $(wc -l < "../.swiftbarignore")"
