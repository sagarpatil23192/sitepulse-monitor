const express = require("express")
const fs = require("fs")

const app = express()

const LOG_FILE = "/app/logs/monitor.log"
const TARGET_URL = process.env.TARGET_URL || "Unknown"

app.set("view engine", "ejs")
app.set("views", __dirname + "/views")

app.get("/", (req, res) => {

    if (!fs.existsSync(LOG_FILE)) {
        return res.render("index", {
            logs: [],
            uptime: 0,
            avgResponse: 0,
            lastStatus: 0,
            targetUrl: TARGET_URL
        })
    }

    const data = fs.readFileSync(LOG_FILE, "utf8").trim().split("\n")

    const logs = data.map(line => {
        const [time, status, response] = line.split(",")

        return {
            time,
            status: parseInt(status) || status,
            response: isNaN(response) ? 0 : parseFloat(response)
        }
    })

    const success = logs.filter(l => l.status == 200).length

    const uptime = logs.length
        ? ((success / logs.length) * 100).toFixed(2)
        : 0

    const avgResponse = logs.length
        ? (
            logs.reduce((a, b) => a + b.response, 0) / logs.length
        ).toFixed(3)
        : 0

    const lastStatus = logs.length ? logs[logs.length - 1].status : 0

    res.render("index", {
        logs,
        uptime,
        avgResponse,
        lastStatus,
        targetUrl: TARGET_URL
    })

})

app.listen(3000, () => {
    console.log("Dashboard running on http://localhost:3000")
})