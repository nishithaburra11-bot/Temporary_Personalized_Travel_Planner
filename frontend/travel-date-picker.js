(() => {
    const input = document.getElementById("startDate");
    const picker = document.getElementById("travelDatePicker");
    const calendar = document.getElementById("travelCalendar");
    const days = document.getElementById("calendarDays");
    const previous = document.getElementById("previousMonth");
    const iso = date => `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
    const today = () => iso(new Date());
    const monthStart = date => new Date(date.getFullYear(), date.getMonth(), 1);
    let month = monthStart(new Date());

    function setValue(value) {
        const parsed = new Date(`${value}T12:00:00`);
        input.value = /^\d{4}-\d{2}-\d{2}$/.test(value || "") && !Number.isNaN(parsed.getTime()) && iso(parsed) === value && value >= today() ? value : "";
    }
    function close() {
        calendar.hidden = true;
        input.setAttribute("aria-expanded", "false");
    }
    function select(value) {
        setValue(value);
        input.dispatchEvent(new Event("change", { bubbles: true }));
        localStorage.removeItem("trip_result");
        close();
        input.focus();
    }
    function render() {
        const minimumMonth = monthStart(new Date());
        if (month < minimumMonth) month = minimumMonth;
        previous.disabled = month <= minimumMonth;
        document.getElementById("calendarMonth").textContent = month.toLocaleDateString(undefined, { month: "long", year: "numeric" });
        days.replaceChildren();
        for (const name of ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]) {
            const label = document.createElement("span");
            label.textContent = name;
            days.append(label);
        }
        for (let i = 0; i < month.getDay(); i++) days.append(document.createElement("span"));
        const count = new Date(month.getFullYear(), month.getMonth() + 1, 0).getDate();
        for (let day = 1; day <= count; day++) {
            const date = new Date(month.getFullYear(), month.getMonth(), day);
            const value = iso(date);
            const button = document.createElement("button");
            button.type = "button";
            button.textContent = day;
            button.disabled = value < today();
            button.setAttribute("aria-label", date.toLocaleDateString(undefined, { dateStyle: "full" }));
            button.setAttribute("aria-pressed", String(input.value === value));
            if (value === today()) button.setAttribute("aria-current", "date");
            button.addEventListener("click", () => {
                if (value < today()) { render(); return; }
                select(value);
            });
            days.append(button);
        }
    }
    function open() {
        setValue(input.value);
        month = monthStart(input.value ? new Date(`${input.value}T12:00:00`) : new Date());
        render();
        calendar.hidden = false;
        input.setAttribute("aria-expanded", "true");
        (days.querySelector('[aria-pressed="true"]') || days.querySelector("button:not(:disabled)")).focus();
    }
    input.addEventListener("click", () => calendar.hidden ? open() : close());
    input.addEventListener("keydown", event => {
        if (["Enter", " ", "ArrowDown"].includes(event.key)) { event.preventDefault(); open(); }
    });
    previous.addEventListener("click", () => {
        if (month > monthStart(new Date())) month = new Date(month.getFullYear(), month.getMonth() - 1, 1);
        render();
    });
    document.getElementById("nextMonth").addEventListener("click", () => {
        month = new Date(month.getFullYear(), month.getMonth() + 1, 1);
        render();
    });
    document.getElementById("calendarToday").addEventListener("click", () => select(today()));
    document.getElementById("calendarClear").addEventListener("click", () => select(""));
    picker.addEventListener("keydown", event => {
        if (event.key === "Escape") { close(); input.focus(); }
    });
    picker.addEventListener("focusout", event => { if (!picker.contains(event.relatedTarget)) close(); });
    document.addEventListener("click", event => { if (!picker.contains(event.target)) close(); });
    window.travelDatePicker = { today, setValue };
})();
