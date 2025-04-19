# 🐦 **Custom Bird Song Training**

This app allows you to practice recognizing bird songs by listening to audio excerpts and identifying the corresponding bird species. The app is developed with **Streamlit** and allows you to select bird species, listen to audio samples from [Xeno-Canto](https://xeno-canto.org/), and display the correct answer after each attempt.

## 🚀 **Features**
- **Species Selection**: Choose one or more bird species to train with.
- **Play Random Song**: Listen to a random song from the selected species.
- **Show Answer**: Reveal the species corresponding to the played song.
- **Replay a Song**: Listen to another song from the same species.

## 💾 **Prerequisites**

Before running the app, make sure you have Python>=3.12 and Poetry installed:

To install the dependencies:

```bash
poetry install
```


## **Data**

To extract a csv file containing links to audio files and species names from [Xeno-Canto](https://xeno-canto.org/), run:

```bash
python scrape_xeno_canto.py
```

You can also create custom `tpo1.csv` and `tpo2.csv` files for specific group selection.

## 🏃‍♂️ **Running the App**

Once you've installed the dependencies and prepared the CSV file, you can launch the app with the following command:

```bash
streamlit run app.py
```

The app will open in your default browser, and you can start practicing recognizing bird songs!

## **Possible Improvements**:
- Improve [Xeno-Canto](https://xeno-canto.org/) query to ensure to get song sounds instead of calls;
- Implement a feature for keeping score;
- Display descriptions for each species' song;
- Implement a feature to save custom species selections.

## 📄 **Contributing**

Contributions are welcome! If you have ideas to improve this app, feel free to open a **pull request** or report any issues via the **issues** section.
