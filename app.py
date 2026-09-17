 
import streamlit as st
import os
import numpy as np
from analyzer import DocumentAnalyzer

st.set_page_config(page_title="National Identity Screening Portal", layout="wide")
st.title("🏛️ Enterprise National Identity Screening System")
st.caption("Secured with PII Masking, Metadata Forensics & Biometric Liveness Detection Layers")

def load_engine():
    return DocumentAnalyzer()

engine = load_engine()

# =====================================================================
# BROWSER SAFETY ALARM SOUND GENERATOR (1000Hz Offline Sine Wave)
# =====================================================================
def trigger_fraud_alarm_buzzer():
    """Generates a sharp 1000Hz digital warning beep with a valid WAV header container format."""
    import io
    import wave

    sample_rate = 44100  # Audio sampling frequency
    duration_seconds = 0.5  # Duration of beep
    frequency_hz = 1000  # Sharp alert pitch tone

    # Mathematically construct the raw sine wave array structures
    time_axis = np.linspace(0, duration_seconds, int(sample_rate * duration_seconds), endpoint=False)
    waveform = np.sin(2 * np.pi * frequency_hz * time_axis)
    audio_signal = (waveform * 32767).astype(np.int16)

    # FIXED: Wrap the raw audio bytes inside a valid WAV file header stream memory structure
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, "wb") as wav_file:
        wav_file.setnchannels(1)  # Mono track channel layout
        wav_file.setsampwidth(2)  # 16-bit PCM configuration parameter
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_signal.tobytes())
    
    audio_binary_stream = wav_buffer.getvalue()

    # Stream the valid audio byte container onto the browser container layout with autoplay forced
    st.audio(audio_binary_stream, format="audio/wav", autoplay=True)

def local_convert_image_to_bytes(img_path):
    try:
        if os.path.exists(img_path):
            with open(img_path, "rb") as file:
                return file.read()
        return None
    except Exception:
        return None

# =====================================================================
# 🔑 UNLOCK BROWSER SOUND GATE (CRUCIAL AUTOPLAY OVERRIDE)
# =====================================================================
st.sidebar.markdown("### 🔊 Audio Alarm System Panel")
audio_authorized = st.sidebar.toggle("🔐 Enable Sound Security Alarms", value=False)
if audio_authorized:
    st.sidebar.success("✅ Browser Audio Channel Activated!")
else:
    st.sidebar.warning("⚠️ Turn this switch ON to allow the fraud buzzer sound to play.")

# Step 1: Upload Layout
col_left, col_right = st.columns(2)
with col_left:
    st.markdown("### 🪪 1. Scan/Upload Citizen ID Card")
    uploaded_card = st.file_uploader("Upload physical card image", type=["jpg", "png", "jpeg"])
with col_right:
    st.markdown("### 🤳 2. Verification Live Selfie Capture")
    uploaded_selfie = st.camera_input("Take Live Biometric Face Scan")

# Run verification layout if both files are submitted
if uploaded_card and uploaded_selfie:
    card_path, selfie_path = "temp_card.jpg", "temp_selfie.jpg"
    masked_card_path = "temp_masked_card.jpg" 
    
    with open(card_path, "wb") as f: f.write(uploaded_card.getbuffer())
    with open(selfie_path, "wb") as f: f.write(uploaded_selfie.getbuffer())
        
    st.markdown("---")
    st.subheader("📊 System Real-Time Security Log Diagnostics")
    
    # Run scanner and draw privacy blocks over sensitive numbers
    extracted_uid = engine.extract_unique_number(card_path, masked_card_path)
    
    col_img, col_rep = st.columns(2)
    with col_img:
        if os.path.exists(masked_card_path):
            st.image(masked_card_path, caption="Masked Document Preview (PII Compliant)", use_container_width=True)
            
            img_bytes = local_convert_image_to_bytes(masked_card_path)
            if img_bytes:
                st.download_button(
                    label="📥 Download Masked ID Compliance Copy",
                    data=img_bytes,
                    file_name=f"redacted_{extracted_uid.lower() if extracted_uid else 'id'}.jpg",
                    mime="image/jpeg",
                    use_container_width=True
                )
        else:
            st.image(uploaded_card, caption="Document Source File", use_container_width=True)
            
        st.image(uploaded_selfie, caption="Captured Live Selfie Stream", width=250)

    with col_rep:
        # 1. Quality Check
        st.markdown("#### 🔍 Module 1: Physical Image Quality Assessment")
        q = engine.check_quality(card_path)
        if q["is_blurry"]: st.error(f"❌ Image is too blurry! (Score: {q['blur_score']})")
        else: st.success(f"✅ Focus Clarity Check Passed ({q['blur_score']})")

        # 2. Metadata Manipulation Scan
        st.markdown("#### 💻 Module 2: Digital Metadata Manipulation Forensics")
        meta = engine.inspect_file_metadata(card_path)
        if meta["is_tampered"]: st.error(f"🚨 TAMPER WARNING: {meta['reason']}")
        else: st.success("✅ File Integrity Scan Passed: No structural modifications detected.")

        # 3. OCR and SQL Database Verification
        st.markdown("#### 🤖 Module 3: Unique ID & Database Verification")
        if not extracted_uid:
            st.error("🚨 System Failure: Unable to locate a valid Unique Identification Number format.")
        else:
            st.success(f"🔍 Extracted Classification Code: **{extracted_uid}**")
            db_record = engine.query_citizen_database(extracted_uid)
            
            if not db_record["found"]:
                st.error(f"🚨 FRAUD ALERT: ID '{extracted_uid}' does not exist in the database repository.")
                if audio_authorized: trigger_fraud_alarm_buzzer()
            elif db_record["status"] != "Active":
                st.warning(f"⚠️ SECURITY ALERT: Citizen account status is marked as **{db_record['status']}**.")
            else:
                st.success(f"✅ Active Database Record Confirmed: Registered to **{db_record['name']}**")
                
                # 4. Liveness Presentation Check
                st.markdown("#### 🧬 Module 4: Passive Biometric Liveness Scan")
                liveness = engine.check_biometric_liveness(selfie_path)
                
                col_score, col_status = st.columns(2)
                with col_score:
                    st.metric(
                        label="Human Liveness Score", 
                        value=f"{liveness['liveness_score']}%",
                        delta="Valid Human" if liveness["is_live_human"] else "Spoof Alert",
                        delta_color="normal" if liveness["is_live_human"] else "inverse"
                    )
                with col_status:
                    if not liveness["is_live_human"]:
                        st.error("🚨 PRESENTATION ATTACK BLOCKED: Spoof signature identified! Real user face not detected.")
                        if audio_authorized: trigger_fraud_alarm_buzzer()
                    else:
                        st.success("✅ Liveness Check Confirmed (Passed Anti-Spoofing Threshold)")

                # Only proceed down the funnel if the user face is confirmed real and organic
                if liveness["is_live_human"]:
                    # 4b. Deepfake Forensic Layer
                    st.markdown("#### 🤖 Module 4b: Deepfake & Synthetic Face Artifact Forensics")
                    with st.spinner("Analyzing micro-texture pixel bleeding structures..."):
                        deepfake_res = engine.detect_deepfake_artifacts(selfie_path)
                        
                    if deepfake_res["is_deepfake"]:
                        st.error(f"🚨 DIGITAL INJECTION ATTACK DETECTED: Generative AI Face-Swap Identified! Access Terminated.")
                        if audio_authorized: trigger_fraud_alarm_buzzer()
                    else:
                        st.success(f"✅ Neural Edge Scan Passed: {deepfake_res['reason']}")

                        # 5. Final Core Biometric Match
                        st.markdown("#### 👤 Module 5: Biometric Profile Face-Binding")
                        bio = engine.verify_photo_biometrics(selfie_path, db_record["photo_path"])
                        
                        if bio.get("status") == "Error":
                            st.warning(f"⚠️ Biometric Scan Blocked: {bio['reason']}")
                        elif bio["is_match"]:
                            st.balloons()
                            st.success(f"🎉 IDENTITY VERIFIED MATCH SUCCEEDED! User matches the central government file with {bio['confidence']}% accuracy.")
                        else:
                            st.error(f"🚨 CRIMINAL IMPERSONATION DETECTED: Face does not match the registered user on file.")
                            if audio_authorized: trigger_fraud_alarm_buzzer()

    # Cleanup memory
    for p in [card_path, selfie_path, masked_card_path]:
        if os.path.exists(p): os.remove(p)
else:
    st.info("💡 Please upload an ID document and capture a live snapshot to run the multi-layered screening mesh.")
