import React from 'react'
import '../table.css'

const Table = ({ data }) => {
    if(data.length==0) return (<div>No items available for this brand or flavor</div>)
    return (
      <table border="1" className='w-full'>
        <thead>
          <tr>
            {Object.keys(data[0]).map((key) => (
              <th key={key}>{key}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, index) => (
            <tr key={index}>
              {Object.values(row).map((value, i) => (
                <td key={i}>{value}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    );
  };
  
  export default Table;