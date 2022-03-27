import { Component, Input } from '@angular/core';

@Component({
  selector: 'posts-grid',
  templateUrl: './posts-grid.component.html',
  styleUrls: ['./posts-grid.component.scss']
})
export class PostsGridComponent {
  @Input() username?: string;

  constructor() { }

}
