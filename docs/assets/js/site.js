/******************************************************************************
 * ISA-SP v2.0
 * site.js
 * DataTables 2.x Core
 ******************************************************************************/

// Retry logic to ensure DataTable is available
const waitForDataTable = (maxAttempts = 100, delayMs = 50) => {
    return new Promise((resolve) => {
        let attempts = 0;
        const checkDataTable = () => {
            if (typeof DataTable !== "undefined") {
                console.log("DataTables 2.x loaded successfully");
                resolve(true);
            } else if (attempts < maxAttempts) {
                attempts++;
                setTimeout(checkDataTable, delayMs);
            } else {
                console.warn("DataTables 2.x did not load within expected time");
                resolve(false);
            }
        };
        checkDataTable();
    });
};

// Wait for DataTable to be available, then initialize
waitForDataTable().then((isAvailable) => {
    if (!isAvailable) {
        console.warn("DataTables 2.x is not available.");
        return;
    }

    document.addEventListener("DOMContentLoaded", () => {
        document.querySelectorAll("table.display").forEach((table) => {

            // ---------- 初始化 DataTable ----------
            let dt = null;
            try {
                dt = new DataTable(table, {
                    ordering: true,
                    searching: true,
                    paging: true,
                    pageLength: 10,
                    autoWidth: false,
                    info: true,
                    scrollX: true,
                    orderCellsTop: true,
                    language: {
                        search: "过滤表格:"
                    }
                });
                
                console.log("DataTable initialized for table:", table.id || "unknown");
                
                // Store dt instance on table element for later reference
                table.DataTableInstance = dt;
                
            } catch (error) {
                console.error("Failed to initialize DataTable for table", table.id, error);
                return;
            }

            // ---------- 添加列过滤行 ----------
            const thead = table.querySelector("thead");
            if (thead && !thead.querySelector(".filters")) {
                const header = thead.rows[0];
                const filter = document.createElement("tr");
                filter.classList.add("filters");

                [...header.cells].forEach((cell, colIndex) => {
                    const th = document.createElement("th");
                    th.innerHTML = '<input type="text" placeholder="过滤..." style="width:100%;box-sizing:border-box;padding:4px;">';
                    filter.appendChild(th);

                    // Get the input element and bind the event
                    const input = th.querySelector("input");
                    if (input && dt) {
                        input.addEventListener("keyup", function () {
                            dt.column(colIndex).search(this.value).draw();
                        });
                        
                        // Also handle input/change events for better responsiveness
                        input.addEventListener("input", function () {
                            dt.column(colIndex).search(this.value).draw();
                        });
                    }
                });

                thead.appendChild(filter);
                console.log("Filter row added for table:", table.id || "unknown");
            }
        });
    });
});