import { Optional } from "@angular/core";

export interface Profile {
    username: string
    full_name: string
    biography: string
    auto_update: boolean
    last_update?: Date
    image_filename: string
}