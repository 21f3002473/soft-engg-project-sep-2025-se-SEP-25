export default function titleCase(str) {
    return str
        .toLowerCase()
        .trim()
        .split(/\s+/)
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(" ");
}