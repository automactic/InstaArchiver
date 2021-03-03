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

  list(offset: number = 0, limit: number = 10) {
    let url = `${environment.apiRoot}/api/posts/`;
    return this.httpClient.get<ListPostsResponse>(url, {params: {offset: String(offset), limit: String(limit)}});
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