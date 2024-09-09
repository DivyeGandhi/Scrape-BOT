export const convertToCSV = (data) => {
    const headers = Object.keys(data[0]);
    const rows = data.map(row => headers.map(header => row[header]));

    let csvContent = "data:text/csv;charset=utf-8,";
    csvContent += headers.join(",") + "\r\n";
    rows.forEach(rowArray => {
        let row = rowArray.join(",");
        csvContent   += row + "\r\n";
    });

    return encodeURI(csvContent);
};