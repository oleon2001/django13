import { ReactNode } from 'react';
import './Table.css';

interface Column<T> {
    id: string;
    label: string;
    minWidth?: number;
    align?: 'right' | 'left' | 'center';
    header: string;
    accessor: keyof T | ((item: T) => ReactNode);
}

interface TableProps<T> {
    columns: Column<T>[];
    data: T[];
}

function Table<T>({ columns, data }: TableProps<T>) {
    return (
        <div className="table-container">
            <table className="table">
                <thead>
                    <tr>
                        {columns.map((column, index) => (
                            <th key={index}>{column.header}</th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {data.map((item, rowIndex) => (
                        <tr key={rowIndex}>
                            {columns.map((column, colIndex) => (
                                <td key={colIndex}>
                                    {typeof column.accessor === 'function'
                                        ? column.accessor(item)
                                        : String(item[column.accessor as keyof T])}
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default Table; 