import fs from "node:fs";
import path from "node:path";

export const changeExtension = (inputFilepath: string, newExtensionWithDot: string): string => {
    if (!newExtensionWithDot.startsWith("."))
        throw new Error("newExtensionWithDot must start with a '.'. For example: '.txt'")

    let base_filename = inputFilepath
    if (inputFilepath.includes(".")) {
        const parts = inputFilepath.split(".")
        parts.pop()
        base_filename = parts.join(".")
    }
    return base_filename + newExtensionWithDot
}

export const readJsonFromFile = (filepath: string, encoding: BufferEncoding = "utf-8"): any  => {
    const buffer = fs.readFileSync(filepath, { encoding: encoding });
    return JSON.parse(buffer.toString())    
}

export const writeJsonToFile = (filepath: string, data: any, encoding: BufferEncoding = "utf-8"): any  => {
    const jsonString = JSON.stringify(data)
    fs.writeFileSync(filepath, jsonString, { encoding: encoding })
}

export const findFilesByExtension = (dirpath: string, extensionWithDot: string): string[] => {
    const found_files: string[] = []

    const isFile = (fileName: string) => {
        return fs.lstatSync(fileName).isFile();
    };

    const isOk = (fileName: string) => {
        return isFile(fileName) && fileName.endsWith(extensionWithDot)
    }

    return fs.readdirSync(dirpath)
        .map(fileName => {
            return path.join(dirpath, fileName);
        })
    .filter(isOk);
}
