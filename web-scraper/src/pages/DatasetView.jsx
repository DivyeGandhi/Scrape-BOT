import React, { useContext } from 'react'
import { ReqdDataContext } from '../context/ReqdDataContext';
import Table from '../components/Table';
import { convertToCSV } from '../utils/csvUtils';

const DatasetView = () => {
    const { reqdData, setReqdData } = useContext(ReqdDataContext);
    console.log(reqdData)
    const downloadCSV = () => {
        const csvContent = convertToCSV(reqdData.list_of_prod);
        const link = document.createElement("a");
        link.setAttribute("href", csvContent);
        link.setAttribute("download", "data.csv");
        document.body.appendChild(link); // Required for FF
        link.click();
        document.body.removeChild(link);
    };
    return (
        (!reqdData.list_of_prod) ?
            <div>Please go back and select the brand and flavor again</div> :
            <div className='w-full'>
                <Table data={reqdData.list_of_prod}/>

                <button className="bg-blue-500 text-white font-bold py-2 px-4 rounded-full mt-4 hover:bg-blue-600 transition duration-200 mt-20" onClick={downloadCSV}>Download CSV file</button>
            </div>
    )
}

export default DatasetView