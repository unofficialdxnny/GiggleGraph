# GiggleGraph 🤣

GiggleGraph is a highly chaotic, good-vibes-only background application that actively listens to your microphone and analyzes your real-time audio for emotions like laughing, crying, cheering, and groaning. When it detects an emotional response, it triggers a cascade of appropriate emojis (😂, 😭, 🎉, 😩) across your screen using a completely transparent, click-through overlay. 

Whether you are watching YouTube, writing code, or in a meeting, your Mac will literally start raining emojis when you find something funny or frustrating.

## What is it made of? 🛠

This project leverages some of the best tools in Python for audio processing, deep learning, and GUI development:

- **[Hugging Face `transformers`](https://huggingface.co/)**: We use the pre-trained `MIT/ast-finetuned-audioset` model (Audio Spectrogram Transformer). This AI model was trained on hundreds of thousands of YouTube audio clips to classify generic audio events rather than just spoken words. This is our "Brain."
- **[`sounddevice`](https://python-sounddevice.readthedocs.io/) & `numpy`**: For accessing the system's microphone natively and efficiently turning audio streams into chunks of numpy arrays. This is our "Ear."
- **[`PyQt6`](https://riverbankcomputing.com/software/pyqt/intro)**: A powerful GUI framework. We use it to create a borderless, transparent, "always-on-top" canvas that ignores mouse clicks. This lets you interact with apps behind the emojis without any obstruction. This is our "Canvas."

## Installation 📦

To run this on your local machine (macOS recommended), follow these steps:

1. **Clone the repository and enter the directory**:
   ```bash
   git clone <your-repo-url>
   cd GiggleGraph
   ```

2. **Create a Virtual Environment** (highly recommended to isolate the large ML dependencies):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install the Requirements**:
   ```bash
   pip install -r requirements.txt
   ```
   > *Note: This will download PyTorch, Transformers, and PyQt6, which are quite large. Grab a coffee!*

## How to Run 🚀

Once everything is installed, ensure your virtual environment is activated, then run the script:

```bash
python giggle_graph.py
```

### First Run
On the first execution, Hugging Face will automatically download the `MIT/ast-finetuned-audioset` model (around ~340MB) and cache it locally.
macOS will likely prompt you asking for **Microphone permissions** for your terminal. You **must click Allow** for the app to hear you.

### Action!
Once the console prints `"Model Loaded!"` and `"Starting audio stream..."`, just start making some noise:
- Giggle or laugh out loud: 😂
- Fake a cry or wail: 😭
- Let out a deep groan or sigh: 😩
- Cheer and clap: 🎉

Watch your screen light up with validation!

## Configuration

If you'd like to tweak the emojis or add new sounds, open `giggle_graph.py` and modify the `EMOJI_MAP` dictionary at the top of the file!

---
*Built with ❤️ and 😂 for the chaotic good programmers.*
