import { Component } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Observable } from 'rxjs';
import { filter, combineLatestWith, switchMap, tap, map } from 'rxjs/operators';

import { PostService, ListPostsResponse, Post } from '../services/post.service';


@Component({
  selector: 'app-posts-grid',
  templateUrl: './posts-grid.component.html',
  styleUrls: ['./posts-grid.component.scss']
})
export class PostsGridComponent {
  username?: string
  year?: string
  month?: string
  response$: Observable<ListPostsResponse>
  selectedPost$: Observable<Post | undefined>
  postService: PostService;

  constructor(private route: ActivatedRoute, postService: PostService) {
    this.postService = postService
    this.response$ = this.route.paramMap.pipe(
      combineLatestWith(this.route.queryParamMap),
      filter(([params, queryParams]) => {
        return (
          this.username == undefined || 
          params.get('username') != this.username || 
          queryParams.get('year') != this.year ||
          queryParams.get('month') != this.month
        )
      }),
      tap(([params, queryParams]) => {
        this.username = params.get('username') ?? undefined
        this.year = queryParams.get('year') ?? undefined
        this.month = queryParams.get('month') ?? undefined
      }),
      switchMap(_ => {
        return postService.list(0, 100, this.username, this.year, this.month)
      })
    )
    this.selectedPost$ = this.route.queryParamMap.pipe(
      map(queryParams => {
        let selected = queryParams.get('selected')
        if (selected) {
          return this.postService.get(selected)
        } else {
          return undefined;
        }
      })
    )
  }
}
