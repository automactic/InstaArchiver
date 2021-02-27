import { Optional } from "@angular/core";

export interface PostsSummary {
  count: number
	earliest_time?: Date
	latest_time?: Date
}

export interface Profile {
	username: string
	full_name: string
	display_name: string
	biography: string
	auto_archive: boolean
	last_scan?: Date
	image_filename: string
	posts?: PostsSummary
}
