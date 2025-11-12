export interface AutocompleteConfig {
    trigger?: string;
    items: string[];
    buttonLabel?: string;
    onInsert: (item: string, currentMessage: string) => string;
}