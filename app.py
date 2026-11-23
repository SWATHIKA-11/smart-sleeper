import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Smart Sleeper", layout="wide")

# Data store (session la irukkum, restart la poidum)
if "journeys" not in st.session_state:
    st.session_state.journeys = []
if "alerts" not in st.session_state:
    st.session_state.alerts = []

st.title("🚌 Smart Sleeper")
st.caption("Smart travel, safer journeys")

role = st.sidebar.radio("Select Portal", ["Passenger", "Staff", "Admin"])

# ---------------- PASSENGER ----------------
if role == "Passenger":
    st.header("Passenger Portal")

    with st.form("journey_form"):
        name = st.text_input("Passenger Name")
        booking_id = st.text_input("Booking ID")
        bus_no = st.text_input("Bus Number (e.g. TN 45 AB 1234)")
        berth = st.text_input("Seat / Berth (e.g. L1, U2)")
        boarding = st.text_input("Boarding Point")
        destination = st.text_input("Destination")
        phone = st.text_input("Phone (10 digits)")
        objects = st.multiselect(
            "Objects you are carrying",
            ["Mobile Phone", "Laptop", "Suitcase", "Handbag", "Wallet", "Charger", "Power Bank"],
        )
        gps = st.checkbox("Enable GPS")
        submit = st.form_submit_button("Save Journey")

    if submit:
        if not name.strip() or not booking_id.strip() or not bus_no.strip() or not destination.strip():
            st.error("Name, Booking ID, Bus Number and Destination are required.")
        elif not (phone.strip().isdigit() and len(phone.strip()) == 10):
            st.error("Phone must be 10 digits.")
        else:
            ids = [j["Booking ID"] for j in st.session_state.journeys]
            if booking_id.strip().upper() in ids:
                st.error("This Booking ID already exists.")
            else:
                st.session_state.journeys.append({
                    "Passenger": name.strip().title(),
                    "Booking ID": booking_id.strip().upper(),
                    "Bus": bus_no.strip().upper(),
                    "Berth": berth.strip().upper(),
                    "Boarding": boarding.strip().title(),
                    "Destination": destination.strip().title(),
                    "Phone": phone.strip(),
                    "Objects": ", ".join(objects),
                    "GPS": "Enabled" if gps else "Disabled",
                })
                st.success("Journey saved!")

    st.subheader("Raise a test object alert")
    ids = [j["Booking ID"] for j in st.session_state.journeys]
    if ids:
        sel = st.selectbox("Booking ID", ids)
        msg = st.text_input("Alert message", "Laptop left on berth")
        if st.button("Raise Alert"):
            st.session_state.alerts.append({"Booking ID": sel, "Message": msg, "Status": "New"})
            st.success("Alert raised.")

# ---------------- STAFF ----------------
elif role == "Staff":
    st.header("Staff Portal")
    bus = st.text_input("Enter your assigned bus number").strip().upper()

    if bus:
        df = pd.DataFrame(st.session_state.journeys)
        if df.empty or bus not in df["Bus"].values:
            st.info("No passengers found for this bus.")
        else:
            bus_df = df[df["Bus"] == bus]

            c1, c2, c3 = st.columns(3)
            c1.metric("Passengers", len(bus_df))
            c2.metric("Destinations", bus_df["Destination"].nunique())
            c3.metric("GPS Enabled", (bus_df["GPS"] == "Enabled").sum())

            st.subheader("Passenger Manifest")
            search = st.text_input("Search by name / booking ID / destination")
            show_df = bus_df
            if search:
                mask = bus_df.apply(
                    lambda r: search.lower() in " ".join(map(str, r.values)).lower(), axis=1
                )
                show_df = bus_df[mask]
            st.dataframe(show_df, use_container_width=True, hide_index=True)

            st.subheader("Passengers by Destination")
            counts = bus_df["Destination"].value_counts()
            fig, ax = plt.subplots()
            ax.bar(counts.index, counts.values, color="#00BFFF")
            ax.set_xlabel("Destination")
            ax.set_ylabel("Passengers")
            st.pyplot(fig)

            st.subheader("Alerts Centre")
            bus_ids = bus_df["Booking ID"].tolist()
            options = ["New", "Checking", "Resolved"]
            for i, a in enumerate(st.session_state.alerts):
                if a["Booking ID"] in bus_ids:
                    col1, col2 = st.columns([3, 1])
                    col1.write(f"**{a['Booking ID']}**: {a['Message']}  →  *{a['Status']}*")
                    new_status = col2.selectbox(
                        "Status", options,
                        index=options.index(a["Status"]),
                        key=f"status_{i}",
                    )
                    st.session_state.alerts[i]["Status"] = new_status

# ---------------- ADMIN ----------------
else:
    st.header("Admin Portal")
    password = st.text_input("Admin Password", type="password")

    if password == "admin123":   # demo password
        df = pd.DataFrame(st.session_state.journeys)
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Journeys", len(df))
        c2.metric("Buses", df["Bus"].nunique() if not df.empty else 0)
        c3.metric("Alerts", len(st.session_state.alerts))

        st.subheader("All Journey Records")
        if df.empty:
            st.info("No journeys yet.")
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.download_button(
                "Download CSV", df.to_csv(index=False).encode("utf-8"),
                file_name="journey_report.csv", mime="text/csv",
            )

        st.subheader("Alert Status")
        if st.session_state.alerts:
            adf = pd.DataFrame(st.session_state.alerts)
            st.dataframe(adf, use_container_width=True, hide_index=True)
            sc = adf["Status"].value_counts()
            fig, ax = plt.subplots()
            ax.bar(sc.index, sc.values, color="#FFB547")
            ax.set_ylabel("Alerts")
            st.pyplot(fig)
    elif password:
        st.error("Wrong password.")