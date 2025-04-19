import streamlit as st
import pandas as pd


@st.cache_data
def load_xeno_canto() -> pd.DataFrame:
    return pd.read_csv("data/xeno_canto.csv")


@st.cache_data
def load_tpo() -> tuple[list[str], list[str]]:
    return pd.read_csv("data/tpo1.csv").squeeze().tolist(), pd.read_csv(
        "data/tpo2.csv"
    ).squeeze().tolist()


all_species_df = load_xeno_canto()
tpo1_list, tpo2_list = load_tpo()

# Select species
available_species = all_species_df["common_name"].unique().tolist()

if "selection" not in st.session_state:
    st.session_state.selection = []


col_tpo1, col_tpo2 = st.columns([0.35, 0.65])
with col_tpo1:
    if st.button("➕ Ajouter les chants TPO1"):
        st.session_state.selection = list(set(st.session_state.selection + tpo1_list))
with col_tpo2:
    if st.button("➕ Ajouter les chants TPO2"):
        st.session_state.selection = list(set(st.session_state.selection + tpo2_list))

selected_species = st.multiselect(
    "Choisissez les espèces à inclure :",
    available_species,
    default=st.session_state.selection,
)

st.session_state.selection = selected_species

selected_species_df = all_species_df[
    all_species_df["common_name"].isin(selected_species)
]


# Play songs
if "current" not in st.session_state:
    st.session_state.current = None

if st.button("🔊 Prendre un chant aléatoire"):
    if not selected_species_df.empty:
        st.session_state.current = selected_species_df.sample(1).iloc[0]
    else:
        st.warning("Veuillez sélectionner au moins une espèce.")

if st.session_state.current is not None:
    audio_url = st.session_state.current["audio_url"]
    st.audio(audio_url)
    st.markdown(
        """
        <script>
        const audio = document.querySelector("audio");
        if (audio) {
            audio.play().catch(() => {});
        }
        </script>
        """,
        unsafe_allow_html=True,
    )

    col_answer, col_replay = st.columns(2)

    with col_answer:
        if st.button("👀 Afficher la réponse"):
            st.success(f"Espèce : **{st.session_state.current['common_name']}**")

    with col_replay:
        if st.button("🔁 Prendre un autre chant de la même espèce"):
            current_species_name = st.session_state.current["common_name"]
            same_species_df = selected_species_df[
                (selected_species_df["common_name"] == current_species_name)
                & (
                    selected_species_df["audio_url"]
                    != st.session_state.current["audio_url"]
                )
            ]

            if not same_species_df.empty:
                st.session_state.current = same_species_df.sample(1).iloc[0]
                st.rerun()
            else:
                st.info("Pas d'autre chant disponible pour cette espèce.")
