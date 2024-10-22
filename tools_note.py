import streamlit as st
from streamlit_option_menu import option_menu
import json
import os

NAV_FILE = "navigation_links.json"
NOTES_FILE = "notes.json"

# Navigation file
def load_navigation():
    if os.path.exists(NAV_FILE):
        with open(NAV_FILE, "r") as f:
            return json.load(f)
    else:
        return {
            "SC": [],
            "Clipper": [],
            "Polri": []
        }

def save_navigation(navigation):
    with open(NAV_FILE, "w") as f:
        json.dump(navigation, f, indent=4)

def load_notes():
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "r") as f:
            return json.load(f)
    else:
        return []

def save_notes(notes):
    with open(NOTES_FILE, "w") as f:
        json.dump(notes, f, indent=4)

navigation = load_navigation()
notes = load_notes()

with st.sidebar:
    st.header("Navigasi Folder")
    
    selected = option_menu(
        menu_title=None,
        options=["SC", "Clipper", "Polri"],
        icons=["folder", "folder", "folder"],
        menu_icon="cast",
        default_index=0,
        orientation="vertical",
    )

    # Menampilkan daftar link di folder yang dipilih
    st.subheader(f"Daftar Link di Folder {selected}")
    if len(navigation[selected]) > 0:
        for link in navigation[selected]:
            st.markdown(f"- [{link['name']}]({link['url']})")
    else:
        st.write("Belum ada link yang ditambahkan.")

    st.markdown("---")

    if st.checkbox("Kelola Navigasi"):
        st.subheader(f"Tambah Link Baru ke Folder {selected}")
        new_link_name = st.text_input("Nama Link Baru")
        new_link_url = st.text_input("URL Link Baru")
        
        if st.button("Tambah Link"):
            if new_link_name and new_link_url:
                navigation[selected].append({"name": new_link_name, "url": new_link_url})
                save_navigation(navigation)
                st.success(f"Link '{new_link_name}' ditambahkan ke folder '{selected}'")
                
                st.session_state['link_added'] = True
            else:
                st.error("Silakan isi nama dan URL link.")
        
        if 'link_added' in st.session_state:
            st.success(f"Link baru ditambahkan ke folder {selected}. Refresh halaman untuk melihat perubahan.")
            del st.session_state['link_added']
        
        st.markdown("---")
        
        st.subheader(f"Edit Nama Link di Folder {selected}")
        for idx, link in enumerate(navigation[selected]):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                new_name = st.text_input(f"Edit nama untuk '{link['name']}'", value=link['name'], key=f"{selected}_{idx}_name")
            with col2:
                if st.button("💾", key=f"{selected}_{idx}_save"):
                    if new_name:
                        navigation[selected][idx]['name'] = new_name
                        save_navigation(navigation)
                        st.success(f"Nama link '{link['name']}' diubah menjadi '{new_name}'")
                        st.session_state['link_edited'] = True
            with col3:
                if st.button("🗑️", key=f"{selected}_{idx}_delete"):
                    del navigation[selected][idx]
                    save_navigation(navigation)
                    st.success(f"Link '{link['name']}' dihapus.")
                    st.session_state['link_deleted'] = True

        if 'link_edited' in st.session_state:
            st.success(f"Link di folder {selected} berhasil diedit.")
            del st.session_state['link_edited']
        
        if 'link_deleted' in st.session_state:
            st.success(f"Link di folder {selected} berhasil dihapus.")
            del st.session_state['link_deleted']

st.header("Dashboard Notes")


MAX_NOTE_LENGTH = 400

with st.form("add_note_form"):
    new_note = st.text_input("Tambahkan Catatan Baru")
    submitted = st.form_submit_button("Tambah")
    if submitted:
        if new_note:
            if len(new_note) <= MAX_NOTE_LENGTH:
                notes.append({"id": len(notes) + 1, "content": new_note})
                save_notes(notes)
                st.success("Catatan ditambahkan!")
            else:
                st.error(f"Catatan terlalu panjang. Maksimal {MAX_NOTE_LENGTH} karakter.")
        else:
            st.error("Silakan masukkan isi catatan.")

st.subheader("Daftar Catatan")

# Daftar Notes
for note in notes:
    st.markdown(f"### Catatan {note['id']}")
    st.write(note['content'])
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button(f"Edit {note['id']}", key=f"edit_{note['id']}"):
            edited_note = st.text_input(f"Edit Catatan {note['id']}", value=note['content'], max_chars=MAX_NOTE_LENGTH, key=f"edit_text_{note['id']}")
            if st.button("Simpan Perubahan", key=f"save_{note['id']}"):
                if edited_note:
                    notes = [n if n['id'] != note['id'] else {"id": n['id'], "content": edited_note} for n in notes]
                    save_notes(notes)
                    st.success(f"Catatan {note['id']} diperbarui.")
                else:
                    st.error("Isi catatan tidak boleh kosong.")
    with col2:
        if st.button(f"Hapus {note['id']}", key=f"delete_{note['id']}"):
            notes = [n for n in notes if n['id'] != note['id']]
            save_notes(notes)
            st.success(f"Catatan {note['id']} dihapus.")
    
    st.markdown("---")
