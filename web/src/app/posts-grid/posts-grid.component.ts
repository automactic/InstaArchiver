import { Component } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { BehaviorSubject, Observable } from 'rxjs';
import { combineLatestWith, distinctUntilChanged, map, switchMap } from 'rxjs/operators';

import { PostService, Post } from '../services/post.service';


@Component({
  selector: 'app-posts-grid',
  templateUrl: './posts-grid.component.html',
  styleUrls: ['./posts-grid.component.scss']
})
export class PostsGridComponent {
  postService: PostService;

  private username?: string
  private year?: string
  private month?: string
  selectedPost$: Observable<Post | null>
  selectedUsername$: Observable<string | null>

  constructor(private route: ActivatedRoute, postService: PostService) {
    this.postService = postService
    this.route.paramMap.pipe(
      combineLatestWith(this.route.queryParamMap),
      map(([params, queryParams]) => {
        return {
          username: params.get('username'),
          year: queryParams.get('year'),
          month: queryParams.get('month'),
        }
      }),
      distinctUntilChanged((previous, current) => {
        return (
          previous.username == current.username && 
          previous.year == current.year && 
          previous.month == current.month
        )
      }),
    ).subscribe((data) => {
      this.username = data.username ?? undefined
      this.year = data.year ?? undefined
      this.month = data.month ?? undefined
      this.postService.shortcodes = []
      this.postService.posts.clear()
      this.getNextPage()
    })
    this.selectedPost$ = this.route.queryParamMap.pipe(
      switchMap(queryParams => {
        let selectedShortcode = queryParams.get('selected')
        let post = this.postService.posts.get(selectedShortcode ?? '')
        if (post) {
          return new BehaviorSubject<Post>(post)
        } else if (selectedShortcode) {
          return this.postService.getPost(selectedShortcode)
        } else {
          return new BehaviorSubject(null)
        }
      })
    )
    this.selectedUsername$ = this.route.paramMap.pipe(
      map(paramMap => paramMap.get('username'))
    )
  }

  getNextPage() {
    this.postService.list(this.postService.posts.size, 100, this.username, this.year, this.month).subscribe(response => {
      response.posts.forEach(post => {
        this.postService.shortcodes.push(post.shortcode)
        this.postService.posts.set(post.shortcode, post)
      })
    })
  }
}
