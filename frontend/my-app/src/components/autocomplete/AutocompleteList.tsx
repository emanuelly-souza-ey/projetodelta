interface AutocompleteListProps {
    query: string;
    items: string[];
    onSelect: (item: string) => void;
    selectedIndex?: number;
}

const AutocompleteList = ({
    query = "",
    items = [],
    onSelect,
    selectedIndex = 0
}: AutocompleteListProps) => {
    const filteredItems = items.filter(item =>
        item.toLowerCase().includes(query.toLowerCase())
    );

    return (
        <div style={{
            position: 'absolute',
            bottom: '100%',
            right: '0',
            width: '250px',
            marginBottom: '8px',
            background: '#2d2d2d',
            border: '1px solid #3a3a3a',
            borderRadius: '8px',
            padding: '8px',
            boxShadow: '0 -4px 12px rgba(0, 0, 0, 0.4)',
            maxHeight: '180px',
            overflowY: 'auto'
        }}>
            {filteredItems.map((item, index) => (
                <div
                    key={item}
                    onClick={() => onSelect(item)}
                    style={{
                        padding: '10px 12px',
                        cursor: 'pointer',
                        borderRadius: '6px',
                        color: '#e0e0e0',
                        transition: 'all 0.2s ease',
                        backgroundColor: index === selectedIndex ? '#4a4a4a' : 'transparent',
                        fontWeight: index === selectedIndex ? 500 : 'normal'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#3a3a3a'}
                    onMouseLeave={(e) => {
                        if (index !== selectedIndex) {
                            e.currentTarget.style.backgroundColor = 'transparent';
                        } else {
                            e.currentTarget.style.backgroundColor = '#4a4a4a';
                        }
                    }}
                >
                    {item}
                </div>
            ))}
        </div>
    );
};

export default AutocompleteList;