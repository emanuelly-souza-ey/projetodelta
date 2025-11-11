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
        <div className="autocomplete-menu">
            {filteredItems.map((item, index) => (
                <div
                    key={item}
                    onClick={() => onSelect(item)}
                    style={{
                        padding: '8px',
                        cursor: 'pointer',
                        backgroundColor: index === selectedIndex ? '#e0e0e0' : 'transparent'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#e0e0e0'}
                    onMouseLeave={(e) => {
                        if (index !== selectedIndex) {
                            e.currentTarget.style.backgroundColor = 'transparent';
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