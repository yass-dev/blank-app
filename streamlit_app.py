import streamlit as st

st.set_page_config(page_title="Streamlit File Upload PoC", page_icon="📤", layout="centered")

st.title("File Upload PoC")
st.write("Sélectionne un ou plusieurs fichiers, puis regarde les requêtes réseau (DevTools/Burp).")

# --- Affichage du session_id (pour le PoC côté serveur) ---
session_id = None
try:
    from streamlit.runtime.scriptrunner import get_script_run_ctx
    ctx = get_script_run_ctx()
    # Selon les versions, l’attribut peut varier; on tente proprement:
    session_id = getattr(ctx, "session_id", None) or getattr(ctx, "session_id", None)
except Exception:
    pass

with st.expander("Debug session"):
    st.write({"session_id": session_id})

# --- Uploader ---
files = st.file_uploader("Upload your files", accept_multiple_files=True)

# On mémorise la liste de fichiers dans la session pour simuler un petit 'panier'
if "uploaded" not in st.session_state:
    st.session_state.uploaded = []

# Quand l’utilisateur sélectionne (ou re-sélectionne) des fichiers
if files:
    # Ajoute ceux qui ne sont pas déjà présents (clé = nom + taille)
    existing_keys = {(f.name, getattr(f, "size", None)) for f in st.session_state.uploaded}
    for f in files:
        key = (f.name, getattr(f, "size", None))
        if key not in existing_keys:
            st.session_state.uploaded.append(f)

st.subheader("Fichiers en session")
if not st.session_state.uploaded:
    st.info("Aucun fichier en session pour l’instant.")
else:
    # Affiche chaque fichier et propose une suppression côté UI
    to_delete = []
    for idx, f in enumerate(st.session_state.uploaded):
        with st.container(border=True):
            st.write(f"**{f.name}** — {getattr(f, 'type', 'application/octet-stream')} — {getattr(f, 'size', 'n/a')} bytes")
            # Aperçu (limité) texte pour PoC
            try:
                content = f.getvalue()[:256]
                if isinstance(content, bytes):
                    try:
                        preview = content.decode("utf-8", errors="replace")
                    except Exception:
                        preview = str(content)
                else:
                    preview = str(content)
                st.code(preview, language="text")
            except Exception:
                pass
            if st.button("🗑️ Supprimer ce fichier", key=f"del-{idx}"):
                to_delete.append(idx)
    # Supprime en fin de boucle (pour éviter les index décalés)
    for i in sorted(to_delete, reverse=True):
        st.session_state.uploaded.pop(i)

# Bouton pour tout nettoyer
if st.button("Reset session state"):
    st.session_state.clear()
    st.success("Session state cleared. Rerun imminent.")
