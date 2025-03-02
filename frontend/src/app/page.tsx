"use client"; 

import { useEffect, useState } from "react";

export default function Home() {
  const [stockData, setStockData] = useState<any>(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/stock/AAPL") 
      .then((data) => setStockData(data))
      .catch((error) => console.error("Error fetching data:", error));
  }, []);

  return (
    <div>
      <h1>FastAPI + React</h1>
      <p>Stock Data: {stockData ? JSON.stringify(stockData) : "Loading..."}</p>
    </div>
    
  );
}
