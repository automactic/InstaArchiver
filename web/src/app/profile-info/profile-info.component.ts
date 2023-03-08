import { Component, Input } from '@angular/core';

import { Profile } from '../services/profile.service';


interface TreeNode<T> {
  data: T;
  children?: TreeNode<T>[];
  expanded?: boolean;
}

interface PostCount {
  year: string
  Q1: number
  Q2: number
  Q3: number
  Q4: number
}

@Component({
  selector: 'profile-info',
  templateUrl: './profile-info.component.html',
  styleUrls: ['./profile-info.component.scss']
})
export class ProfileInfoComponent {
  @Input() profile?: Profile
  allColumns = ['Year', 'Q4', 'Q3', 'Q2', 'Q1']
  postCounts: TreeNode<PostCount>[] = []

  constructor() { }

  ngOnChanges(changes: any) {
    let profile = changes.profile.currentValue
    if (profile) {
      this.postCounts = Object.keys(profile.counts ?? {}).map(key => {
        let count = profile.counts[key] ?? {}
        return {
          data: {
            year: key,
            Q1: count['Q1'],
            Q2: count['Q2'],
            Q3: count['Q3'],
            Q4: count['Q4'],
          }
        }
      }).sort((lhs, rhs) => lhs.data.year < rhs.data.year ? 1 : -1)
    } else {
      this.postCounts = []
    }
  }
}
