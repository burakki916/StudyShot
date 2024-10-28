#!/usr/bin/env sh

# Define paths
scrDir="$(dirname "$(realpath "$0")")"
source "${scrDir}/globalcontrol.sh"
studyShotFolder="/home/rakki/RakkiDrive/StudyShot" 
subjectFile="$studyShotFolder/subjects.txt"  # Path to the subjects file
imageDir="$studyShotFolder/images"  # Path to the subjects file
tempScreenshot1directory="/tmp/tempScreenshot1.png"
tempScreenshot2directory="/tmp/tempScreenshot2.png"




# Ensure the subjects file exists
if [ ! -f "$subjectFile" ]; then
    touch "$subjectFile"  # Create the file if it doesn't exist
fi

# Take screenshots
grimblast copysave area "$tempScreenshot1directory"
grimblast copysave area "$tempScreenshot2directory"

# Read subjects into an array
mapfile -t subjects < "$subjectFile"  # Read the subjects into an array
subject_count=${#subjects[@]}

# Prepare rofi input
options=()
for subject in "${subjects[@]}"; do
    options+=("$subject")
done

options+=("Create a new subject")  # Option to create a new subject
# Use rofi to prompt the user for a subject

style="$1"  # Capture the style argument
roconf="$HOME/.config/rofi/styles/style_12.rasi"  # Construct the full path to the style file


selected_subject=$(printf '%s\n' "${options[@]}" | rofi -dmenu -theme "${roconf}" -p "Select a subject:")

if [ "$selected_subject" = "Create a new subject" ]; then
    new_subject=$(echo "" | rofi -dmenu -theme "${roconf}" -p "Enter new subject name:")
    if [ -n "$new_subject" ]; then
        echo "$new_subject" >> "$subjectFile"  # Add new subject to the file
        subject_name="$new_subject"
    else
        echo "No subject entered. Exiting."
        exit 1
    fi
else
    subject_name="$selected_subject"
fi

# Move the screenshot files to the subject directory
date=$(date +'%Y-%m-%d_%H-%M-%S')
mkdir -/f "$imageDir/"
mv "$tempScreenshot1directory" "$imageDir/${subject_name}-${date}-front.png"
mv "$tempScreenshot2directory" "$imageDir/${subject_name}-${date}-back.png"
