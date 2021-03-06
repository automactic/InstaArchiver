import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { environment } from '../../environments/environment';


export interface Post {
  shortcode: string
  owner_username: string
  creation_time: Date
  caption: string
	items: PostItem[]
}

export interface PostItem {
  index: number
  type: string
  duration: number
  filename: string
  thumb_image_filename: string
}

export interface ListPostsResponse {
  posts: Post[]
  limit: number
  offset: number
  count: number
}


@Injectable({
  providedIn: 'root'
})
export class PostService {
  constructor(private httpClient: HttpClient) { }

  list(offset: number = 0, limit: number = 10, username?: string, year?: string, month?: string) {
    let url = `${environment.apiRoot}/api/posts/`;
    let params: Record<string, string> = { offset: String(offset), limit: String(limit) };
    if (username) { params.username = username }
    if (year && month) {
      params.start_time = new Date(+year, +month - 1, 1).toISOString();
      params.end_time = new Date(+month == 12 ? +year + 1 : +year, +month == 12 ? 0 : +month, 1).toISOString();
    } else if ( year && !month ) {
      params.start_time = new Date(+year, 0, 1).toISOString();
      params.end_time = new Date(+year + 1, 0, 1).toISOString();
    }
    return this.httpClient.get<ListPostsResponse>(url, {params: params});
  }

  delete(shortcode: string, itemIndex: number) {
    let url = `${environment.apiRoot}/api/posts/${shortcode}/${itemIndex}/`;
    return this.httpClient.delete(url);
  }

  getMediaPath(username: string, filename: string): string {
    return `${environment.apiRoot}/media/posts/${username}/${filename}`;
  }

  getPosterPath(username: string, filename: string): string {
    return `${environment.apiRoot}/media/thumb_images/${username}/${filename}`;
  }
}