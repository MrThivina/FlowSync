const http = require("http");
const fs = require("fs");
const path = require("path");

const root = __dirname;
const dbPath = path.join(root, "pos_data.json");
const port = 8000;

const defaultState = {
    products: [
        { id: 1, sku: "1001", name: "Organic Banana Bundle", department: "Produce", price: 2.99, cost: 1.35, unit: "bunch", stock: 28, reorder: 12, icon: "BN" },
        { id: 2, sku: "1002", name: "Red Apple Pack", department: "Produce", price: 4.49, cost: 2.1, unit: "1 kg", stock: 34, reorder: 10, icon: "AP" },
        { id: 3, sku: "2101", name: "Whole Milk 1L", department: "Dairy", price: 1.89, cost: 0.96, unit: "bottle", stock: 9, reorder: 16, icon: "MK" },
        { id: 4, sku: "2102", name: "Greek Yogurt Cup", department: "Dairy", price: 1.25, cost: 0.58, unit: "cup", stock: 22, reorder: 14, icon: "YG" },
        { id: 5, sku: "3201", name: "Sourdough Loaf", department: "Bakery", price: 3.75, cost: 1.7, unit: "loaf", stock: 17, reorder: 8, icon: "BR" },
        { id: 6, sku: "3202", name: "Butter Croissant", department: "Bakery", price: 1.65, cost: 0.72, unit: "each", stock: 15, reorder: 8, icon: "CR" },
        { id: 7, sku: "4401", name: "Basmati Rice 5kg", department: "Grocery", price: 12.8, cost: 8.6, unit: "bag", stock: 8, reorder: 10, icon: "RC" },
        { id: 8, sku: "4402", name: "Canned Tuna", department: "Grocery", price: 2.4, cost: 1.2, unit: "can", stock: 44, reorder: 18, icon: "TN" },
        { id: 9, sku: "5501", name: "Laundry Detergent", department: "Household", price: 8.99, cost: 5.1, unit: "2L", stock: 13, reorder: 10, icon: "LD" },
        { id: 10, sku: "5502", name: "Paper Towel 6 Roll", department: "Household", price: 6.5, cost: 3.8, unit: "pack", stock: 20, reorder: 12, icon: "PT" },
        { id: 11, sku: "6601", name: "Chicken Breast 1kg", department: "Meat", price: 7.95, cost: 4.4, unit: "pack", stock: 19, reorder: 9, icon: "CH" },
        { id: 12, sku: "7701", name: "Orange Juice 1L", department: "Beverage", price: 3.2, cost: 1.65, unit: "carton", stock: 26, reorder: 12, icon: "OJ" }
    ],
    customers: [
        { id: 1, name: "Walk-in Customer", phone: "", email: "", points: 0, tier: "None" },
        { id: 2, name: "Amanda Silva", phone: "555-0144", email: "amanda@example.com", points: 420, tier: "Gold" },
        { id: 3, name: "Noah Perera", phone: "555-0191", email: "noah@example.com", points: 160, tier: "Silver" },
        { id: 4, name: "Maya Chen", phone: "555-0178", email: "maya@example.com", points: 92, tier: "Member" }
    ],
    transactions: [
        { id: "R-10038", time: "2026-05-13 09:14", customerId: 2, payment: "Card", status: "Paid", items: [{ id: 2, quantity: 2 }, { id: 8, quantity: 4 }, { id: 10, quantity: 1 }] },
        { id: "R-10039", time: "2026-05-13 11:27", customerId: 1, payment: "Cash", status: "Paid", items: [{ id: 5, quantity: 2 }, { id: 6, quantity: 6 }, { id: 12, quantity: 2 }] },
        { id: "R-10040", time: "2026-05-13 13:45", customerId: 3, payment: "Mobile", status: "Paid", items: [{ id: 7, quantity: 1 }, { id: 3, quantity: 3 }, { id: 1, quantity: 2 }] }
    ],
    heldSales: [],
    cart: [[1, 2], [3, 1], [5, 1]],
    customerId: 1,
    payment: "Card",
    activeView: "sales",
    activeDepartment: "All",
    registerOpen: true,
    taxRate: 0.08,
    nextReceipt: 10041
};

function ensureDb() {
    if (!fs.existsSync(dbPath)) {
        fs.writeFileSync(dbPath, JSON.stringify(defaultState, null, 2));
    }
}

function loadState() {
    ensureDb();
    return JSON.parse(fs.readFileSync(dbPath, "utf8"));
}

function saveState(payload) {
    fs.writeFileSync(dbPath, JSON.stringify(payload, null, 2));
}

function sendJson(res, status, payload) {
    const body = JSON.stringify(payload);
    res.writeHead(status, {
        "Content-Type": "application/json",
        "Content-Length": Buffer.byteLength(body),
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,PUT,POST,OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    });
    res.end(body);
}

function readBody(req) {
    return new Promise((resolve, reject) => {
        let body = "";
        req.on("data", (chunk) => {
            body += chunk;
            if (body.length > 5_000_000) {
                reject(new Error("Request body is too large"));
                req.destroy();
            }
        });
        req.on("end", () => resolve(body));
        req.on("error", reject);
    });
}

function contentType(filePath) {
    const ext = path.extname(filePath).toLowerCase();
    if (ext === ".html") return "text/html; charset=utf-8";
    if (ext === ".css") return "text/css; charset=utf-8";
    if (ext === ".js") return "text/javascript; charset=utf-8";
    if (ext === ".json") return "application/json; charset=utf-8";
    return "application/octet-stream";
}

function serveFile(res, requestPath) {
    const cleanPath = requestPath === "/" ? "/panel.html" : requestPath;
    const filePath = path.normalize(path.join(root, cleanPath));
    if (!filePath.startsWith(root)) {
        res.writeHead(403);
        res.end("Forbidden");
        return;
    }
    fs.readFile(filePath, (error, data) => {
        if (error) {
            res.writeHead(404);
            res.end("Not found");
            return;
        }
        res.writeHead(200, { "Content-Type": contentType(filePath) });
        res.end(data);
    });
}

const server = http.createServer(async (req, res) => {
    if (req.method === "OPTIONS") {
        res.writeHead(204, {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,PUT,POST,OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        });
        res.end();
        return;
    }

    if (req.url === "/api/state" && req.method === "GET") {
        sendJson(res, 200, loadState());
        return;
    }

    if (req.url === "/api/state" && req.method === "PUT") {
        try {
            const payload = JSON.parse(await readBody(req));
            saveState(payload);
            sendJson(res, 200, { ok: true });
        } catch (error) {
            sendJson(res, 400, { ok: false, error: error.message });
        }
        return;
    }

    if (req.url === "/api/reset" && req.method === "POST") {
        saveState(defaultState);
        sendJson(res, 200, defaultState);
        return;
    }

    serveFile(res, decodeURI(req.url.split("?")[0]));
});

ensureDb();
server.listen(port, "localhost", () => {
    console.log(`FlowSync POS backend running at http://localhost:${port}`);
    console.log(`Data file: ${dbPath}`);
});
