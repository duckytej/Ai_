import re
import unicodedata

input_file = r"D:\data\discord\Direct Messages - aJ [848764782700920893].html"
output_file = r"C:\Users\steja\GitHub\Ai\Ai\note\cleane.txt"

# Map usernames to roles
user_aliases = ["ducky_tej"]
assistant_aliases = ["anuzzga"]

# Patterns to remove from message content
patterns_to_remove = [
    r"https?://\S+",  # Links
    r"\{Attachments\}.*",  # Discord attachment placeholder
    r"\{embed\}.*",
    r"\{Reactions\}.*", # Discord reactions placeholder
    r"<Media omitted>",
    r"<This message was edited>",
    r"You deleted this message" # Tagging pattern
]

combined_remove_pattern = re.compile("(" + "|".join(patterns_to_remove) + ")", re.IGNORECASE)

# Match timestamp + username, strip "(pinned)" if present
header_pattern = re.compile(r"^\[(\d{2}-\d{2}-\d{4} \d{2}:\d{2})\] ([^\(]+?)(?: \(pinned\))?$")

def clean_message(msg):
    msg = unicodedata.normalize("NFKC", msg)
    msg = combined_remove_pattern.sub("", msg)
    msg = re.sub(r"\s+", " ", msg).strip()
    return msg

def process_chat(input_path, output_path):
    cleaned_blocks = []
    last_speaker = None
    current_block = []

    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        header_match = header_pattern.match(line)
        if header_match:
            timestamp, username = header_match.groups()
            # Collect following lines as the message body
            i += 1
            body_lines = []
            while i < len(lines) and not header_pattern.match(lines[i]):
                body_lines.append(lines[i].strip())
                i += 1
            message = clean_message(" ".join(body_lines))
            if not message:
                continue

            # Determine speaker
            if username.lower() in [u.lower() for u in user_aliases]:
                speaker = "<|user|>"
            elif username.lower() in [a.lower() for a in assistant_aliases]:
                speaker = "<|assistant|>"
            else:
                continue

            # Merge consecutive same-speaker messages
            if speaker == last_speaker:
                current_block.append(message)
            else:
                if current_block:
                    cleaned_blocks.append(f"{last_speaker}\n" + "\n".join(current_block))
                current_block = [message]
                last_speaker = speaker
        else:
            i += 1

    if current_block:
        cleaned_blocks.append(f"{last_speaker}\n" + "\n".join(current_block))

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(cleaned_blocks))
        print(cleaned_blocks[-1])

    print(f"Cleaned and merged data saved to {output_path}")

if __name__ == "__main__":
    process_chat(input_file, output_file)
