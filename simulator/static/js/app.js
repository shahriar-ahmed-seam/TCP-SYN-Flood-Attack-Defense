document.addEventListener("DOMContentLoaded", () => {
  const elStatus = document.getElementById("status-indicator");
  const elStatusText = document.getElementById("status-text");

  const elKpiBacklog = document.getElementById("kpi-backlog");
  const elKpiBacklogSub = document.getElementById("kpi-backlog-sub");
  const elKpiLatency = document.getElementById("kpi-latency");
  const elKpiLatencySub = document.getElementById("kpi-latency-sub");
  const elKpiRate = document.getElementById("kpi-rate");
  const elKpiDefense = document.getElementById("kpi-defense");

  const btnStart = document.getElementById("btn-start");
  const btnStop = document.getElementById("btn-stop");
  const sliderRate = document.getElementById("slider-rate");
  const valRate = document.getElementById("val-rate");
  const swSyncookies = document.getElementById("sw-syncookies");
  const swIptables = document.getElementById("sw-iptables");
  const selBacklog = document.getElementById("sel-backlog");

  const canvas = document.getElementById("latency-canvas");
  const logTbody = document.getElementById("log-tbody");

  const topoAttacker = document.getElementById("topo-attacker-sub");
  const topoVictim = document.getElementById("topo-victim-sub");
  const topoClient = document.getElementById("topo-client-sub");

  let logFingerprint = "";

  sliderRate.addEventListener("input", (e) => {
    valRate.textContent = `${Number(e.target.value).toLocaleString()} pps`;
  });

  btnStart.addEventListener("click", () => {
    fetch("/api/attack/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ rate_pps: parseInt(sliderRate.value, 10) })
    });
  });

  btnStop.addEventListener("click", () => {
    fetch("/api/attack/stop", { method: "POST" });
  });

  swSyncookies.addEventListener("change", (e) => {
    fetch("/api/defense/syncookies", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ enable: e.target.checked })
    });
  });

  swIptables.addEventListener("change", (e) => {
    fetch("/api/defense/iptables", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ enable: e.target.checked })
    });
  });

  selBacklog.addEventListener("change", (e) => {
    fetch("/api/config/backlog", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ size: parseInt(e.target.value, 10) })
    });
  });

  async function poll() {
    try {
      const res = await fetch("/api/status");
      if (res.ok) {
        const data = await res.json();
        render(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setTimeout(poll, 300);
    }
  }

  function render(data) {
    elStatus.className = "status-indicator";
    if (data.status === "ATTACK") {
      elStatus.classList.add("attack");
      elStatusText.textContent = "SYN Flood Active (Saturation)";
    } else if (data.status === "DEFENDED") {
      elStatus.classList.add("defended");
      elStatusText.textContent = "Mitigation Active";
    } else {
      elStatusText.textContent = "Normal Traffic";
    }

    elKpiBacklog.textContent = `${data.victim.syn_recv} / ${data.victim.backlog_limit}`;
    elKpiBacklogSub.textContent = `${data.victim.saturation_pct}% queue saturation`;

    const lat = data.client.latency_ms;
    elKpiLatency.textContent = `${lat} ms`;
    elKpiLatency.style.color = (lat >= 400) ? "var(--color-rose)" : (lat >= 100) ? "var(--color-amber)" : "var(--text-main)";
    elKpiLatencySub.textContent = `${data.client.availability_pct}% availability (${data.client.status})`;

    elKpiRate.textContent = data.attacker.active ? `${Number(data.attacker.rate_pps).toLocaleString()} pps` : "0 pps";

    const sc = data.defense.syncookies ? "SYN Cookies: ON" : "SYN Cookies: OFF";
    const ipt = data.defense.iptables ? `iptables: ON (${data.defense.iptables_dropped} dropped)` : "iptables: OFF";
    elKpiDefense.textContent = `${sc} | ${ipt}`;

    btnStart.disabled = data.attacker.active;
    btnStop.disabled = !data.attacker.active;
    if (document.activeElement !== swSyncookies) {
      swSyncookies.checked = data.defense.syncookies;
    }
    if (document.activeElement !== swIptables) {
      swIptables.checked = data.defense.iptables;
    }

    topoAttacker.textContent = data.attacker.active ? `FLOODING (${data.attacker.packets_sent} pkts)` : "IDLE";
    topoVictim.textContent = `${data.victim.syn_recv}/${data.victim.backlog_limit} SYN_RECV`;
    topoClient.textContent = `${data.client.latency_ms}ms (${data.client.status})`;

    LineChart.draw(canvas, data.client.history);

    const fp = JSON.stringify(data.logs);
    if (fp !== logFingerprint) {
      logFingerprint = fp;
      logTbody.innerHTML = "";
      data.logs.slice().reverse().forEach(entry => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${entry.time}</td>
          <td><span class="log-tag ${entry.source}">${entry.source}</span></td>
          <td>${entry.message}</td>
        `;
        logTbody.appendChild(tr);
      });
    }
  }

  poll();
});
