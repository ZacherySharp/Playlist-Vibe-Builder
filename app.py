import gradio as gr

# --- DATA ---
# A list of songs. Each song is a list: [title, artist, energy, duration_seconds]
songs = [
    ["Blinding Lights",  "The Weeknd",     92, 200],
    ["drivers license",  "Olivia Rodrigo", 43, 242],
    ["Good 4 U",         "Olivia Rodrigo", 88, 178],
    ["Stay",             "Kid LAROI",      65, 141],
    ["Peaches",          "Justin Bieber",  56, 198],
    ["Levitating",       "Dua Lipa",       78, 203],
    ["Montero",          "Lil Nas X",      85, 137],
]

# --- MERGE SORT ---
# I implement merge sort myself. I do NOT use sorted() or list.sort().

def merge(left, right, key_index):
    """Merge two sorted lists into one sorted list."""
    result = []
    i = 0
    j = 0

    while i < len(left) and j < len(right):
        # Compare the chosen key (energy or duration)
        if left[i][key_index] <= right[j][key_index]:
            result.append(left[i])
            i = i + 1
        else:
            result.append(right[j])
            j = j + 1

    # Add any remaining items
    while i < len(left):
        result.append(left[i])
        i = i + 1
    while j < len(right):
        result.append(right[j])
        j = j + 1

    return result


def merge_sort(lst, key_index):
    """Recursively split the list in half, sort each half, then merge."""
    # Base case: a list of 0 or 1 items is already sorted
    if len(lst) <= 1:
        return lst

    mid = len(lst) // 2
    left  = merge_sort(lst[:mid], key_index)   # sort left half
    right = merge_sort(lst[mid:], key_index)   # sort right half

    return merge(left, right, key_index)        # merge both halves


def merge_sort_with_steps(lst, key_index):
    """
    Run merge sort and record every merge as a step.
    Returns a list of snapshots so the user can see each stage.
    """
    steps = []

    def merge_and_record(left, right):
        result = []
        i = 0
        j = 0

        while i < len(left) and j < len(right):
            if left[i][key_index] <= right[j][key_index]:
                result.append(left[i])
                i = i + 1
            else:
                result.append(right[j])
                j = j + 1

        while i < len(left):
            result.append(left[i])
            i = i + 1
        while j < len(right):
            result.append(right[j])
            j = j + 1

        # Save a snapshot of the merged group
        steps.append(result[:])
        return result

    def sort_and_record(lst):
        if len(lst) <= 1:
            return lst
        mid   = len(lst) // 2
        left  = sort_and_record(lst[:mid])
        right = sort_and_record(lst[mid:])
        return merge_and_record(left, right)

    sort_and_record(lst[:])   # work on a copy
    return steps


# --- GRADIO FUNCTIONS ---

def sort_playlist(sort_by):
    """Sort the playlist and return the result as a table."""
    # Choose which column to sort by
    if sort_by == "Energy (0-100)":
        key_index = 2
        key_name  = "energy"
    else:
        key_index = 3
        key_name  = "duration"

    # Run merge sort
    sorted_songs = merge_sort([row[:] for row in songs], key_index)

    # Build a readable table
    table = []
    for i, song in enumerate(sorted_songs):
        mins = song[3] // 60
        secs = song[3] % 60
        table.append([
            i + 1,
            song[0],
            song[1],
            song[2],
            f"{mins}:{secs:02d}",
        ])

    message = f"✅ Sorted by {key_name} using Merge Sort! Showing low → high."
    return table, message


def show_steps(sort_by):
    """Show each merge step so the user can follow the algorithm."""
    if sort_by == "Energy (0-100)":
        key_index = 2
    else:
        key_index = 3

    steps = merge_sort_with_steps([row[:] for row in songs], key_index)

    # Build a text description of each step
    output = ""
    for i, group in enumerate(steps):
        titles = [s[0] for s in group]
        values = [s[key_index] for s in group]
        pairs  = [f"{t} ({v})" for t, v in zip(titles, values)]
        output += f"Step {i+1}: merged → {', '.join(pairs)}\n"

    return output


# --- GRADIO UI ---

with gr.Blocks(title="Playlist Vibe Builder") as demo:

    gr.Markdown("# 🎵 Playlist Vibe Builder")
    gr.Markdown("Sort a playlist using **Merge Sort**. Choose a sort key, then click a button.")

    sort_by = gr.Radio(
        choices=["Energy (0-100)", "Duration (seconds)"],
        value="Energy (0-100)",
        label="Sort by"
    )

    with gr.Row():
        btn_sort  = gr.Button("Sort Playlist",  variant="primary")
        btn_steps = gr.Button("Show Sort Steps")

    status = gr.Textbox(label="Status", interactive=False)

    result_table = gr.Dataframe(
        headers=["#", "Title", "Artist", "Energy", "Duration"],
        label="Sorted Playlist",
    )

    steps_box = gr.Textbox(
        label="Merge Sort Steps (each line = one merge)",
        lines=10,
        interactive=False,
    )

    btn_sort.click(
        fn=sort_playlist,
        inputs=[sort_by],
        outputs=[result_table, status],
    )

    btn_steps.click(
        fn=show_steps,
        inputs=[sort_by],
        outputs=[steps_box],
    )

demo.launch()
